#!/usr/bin/expect

proc tgrep {pattern filename} {
set fp [open $filename r]
while { [gets $fp line]>0 } {
   puts $line
   if { [regexp $pattern $line] } {
    puts stdout $line
    }
}
close $fp
}


tgrep {(0-9a-zA-Z)+} test1.txt
