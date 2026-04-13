ffplay -f lavfi "amovie=oscillart.webm,asplit[a][b];[a]avectorscope=mode=lissajous:size=400x400:rate=144[v];[v]colorkey=0xffffff:0.1:0.1[out0];[b]anullsink"
