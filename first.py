import subprocess
from subprocess import PIPE
from threading import Thread

try:
    from queue import Queue, Empty
except:
    from Queue import Queue, Empty

# This creates a queue object and a function to put properly formatted stuff in it
q = Queue()


# Extremely hacky awesome thing that is awesome
def runOutputUntilDone(process, cmd, timeout=20, queue=q, done_message="done"):
    res = []
    process.stdin.write((cmd + ";Write-Host " + done_message + "\n").encode("utf-8"))
    process.stdin.flush()
    # FIXME : Sometimes causes an error if powershell decides to not respond
    queue.get(
        timeout=timeout
    )  # This is to get rid of the line that automatically comes when entering stuff in powershell.
    try:
        current_line = queue.get(timeout=timeout)
        while current_line:
            if current_line.strip() == done_message:
                return res
            print(
                "Output from PowerShell process: " + current_line.strip()
            )  # This is for debugging purposes
            res.append(current_line)
            current_line = q.get(timeout=timeout)
    except Empty:
        return res


def enqueueOutput(out, queue):
    for line in iter(out.readline, b""):
        queue.put(line.decode("utf-8"))
    out.close()


def main():

    # This creates a powershell subprocess
    ps = subprocess.Popen(["powershell"], stdin=PIPE, stderr=PIPE, stdout=PIPE)

    # This creates a thread responsible for taking the output from the powershell process and putting it in a queue
    ps_thread = Thread(target=enqueueOutput, args=(ps.stdout, q))
    ps_thread.daemon = True
    ps_thread.start()

    # This starts the powershell process, command sent to it really doesn't matter, it just needs to have something sent to stdin to start
    runOutputUntilDone(
        process=ps,
        cmd="Write-Host Booting up...",
        timeout=5,
        queue=q,
        done_message="done",
    )

    # Do whatever from here, below line is an example
    fonts = runOutputUntilDone(
        process=ps,
        cmd="chcp 65001|Out-Null;Add-Type -AssemblyName PresentationCore;$families=[Windows.Media.Fonts]::SystemFontFamilies;foreach($family in $families){$name='';if(!$family.FamilyNames.TryGetValue([Windows.Markup.XmlLanguage]::GetLanguage('zh-cn'),[ref]$name)){$name=$family.FamilyNames[[Windows.Markup.XmlLanguage]::GetLanguage('en-us')]}echo $name}",
        timeout=5,
        queue=q,
        done_message="done",
    )

    for font in fonts:
        print(font.replace("\r\n", ""))


if __name__ == "__main__":
    main()
