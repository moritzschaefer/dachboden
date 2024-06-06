import librosa

#ad_path = 'fillyourbrains.mp3'
#ad_path = 'Purdie - Original Mix.mp3'
ad_path = 'song.mp3'

y, sr = librosa.load(ad_path)
y = librosa.to_mono(y)

print("y:", y)
print("sr:", sr)
tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
#
print('T: ',tempo, 'BPM')
