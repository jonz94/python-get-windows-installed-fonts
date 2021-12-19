import subprocess

# https://superuser.com/a/1610376/1580032
powershellScript = "chcp 65001|Out-Null;Add-Type -AssemblyName PresentationCore;$families=[Windows.Media.Fonts]::SystemFontFamilies;foreach($family in $families){$name='';if(!$family.FamilyNames.TryGetValue([Windows.Markup.XmlLanguage]::GetLanguage('zh-cn'),[ref]$name)){$name=$family.FamilyNames[[Windows.Markup.XmlLanguage]::GetLanguage('en-us')]}echo $name}"

cmd = f'powershell.exe -Command "{powershellScript}"'

# https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output
output = subprocess.run(cmd, capture_output=True).stdout.decode("utf-8")

print(list(filter(lambda line: line != "", output.split("\r\n"))))
