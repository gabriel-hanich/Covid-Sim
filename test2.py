from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt

a = []
noise = PerlinNoise(octaves= 5)
for x in range(100):
        a.append(noise([x / 100]))

plt.plot(a)
plt.show()