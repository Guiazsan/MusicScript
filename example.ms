speed = 110bpm
beat = 4/4
tone = C

instrument drum {
    kind : percursion
    timbre : studioDrum1
}

instrument bass {
    timbre : slapBass3
    pitch : 2
}

instrument piano {
    timbre : brightPiano
    pitch : 3
}

instrument saxSolo {
    timbre : AltoSax
    pitch : 3
}

session drumIntro {
    drum(8(b,cr),8ch,8(sn,ch),8ch,8(b,ch),8(b,ch),8(sn,ch),8oh)
}

session drumLine {
    drum(8(b,ch),8ch,8(sn,ch),8ch,8(b,ch),8(b,ch),8(sn,ch),8oh)
}

session intro {
    play(drumIntro, drumLine)
    bass(4c+8,8c,4g+8,8g,4f+8,8f,4c+8,8c)
    piano(2cM,2gM,2fM,2cM)
}

play(intro)