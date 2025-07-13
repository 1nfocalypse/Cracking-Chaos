<p align="center">
  <a href="https://github.com/1nfocalypse/Cracking-Chaos">
	<img alt="Cracking Chaos" src="https://i.imgur.com/XKrgRpG.png"/>
  </a>
</p>
<p align="center">
  <a href="https://choosealicense.com/licenses/mit/">
  	<img alt="License: MIT" src="https://img.shields.io/github/license/1nfocalypse/Cracking-Chaos"/>
  </a>
</p>
<h2 align="center">Cracking Chaos</h2>
<h3 align="center">
  Design, Use, and Exploitation of Pseudo-random Number Generators
</h3>
<p align="center">
  By <a href="https://github.com/1nfocalypse">1nfocalypse</a>
</p>

## What is this project?
*Cracking Chaos* is a survey of PRNGs, including a paper and several implemented demos. It is intended to showcase not only the different types of PRNGs, but also how they work, how they should be used, and, in some cases, how they fail. While not a completely comprehensive reference work, Cracking Chaos shows off a wide variety of generators, ranging from
Linear Congruential Generators to the infamous backdoored DUAL_EC_DRBG. As an additional disclaimer, there are no claims made to the security of the generators implemented here. All code provided is for educational purposes only. Use at your own risk.

[Read the paper here!](./Cracking-Chaos-Making-Using-and-Breaking-PRNGs.pdf)

## Highlights
- 14 page paper as a theoretical survey
- Inversion of MT19937
- LCG inversion via Marsaglia's Theorem
- LFSR inversion via Berlekamp-Massey
- RC4 second byte bias visualized
- A working implementation of the DUAL_EC_DRBG backdoor on Curve M-383
- From-scratch (or very nearly) implementations of 10 different PRNGs in Python3
- All implementations are annotated whenever possible for clarity

## Who is this for?
This project was originally developed for DEFCON 33's Cryptography and Privacy Village, presented as "Cracking Chaos: Making, Using, and Breaking PRNGs". It has been made completely public as both a reference
for attendees and as an educational tool for the wider public. When made public, the recording of the talk will also be linked here.

Ideally, it should be useful to:
- Engineers who want to thoroughly understand the PRNGs they're using, or implement them themselves.
- Hackers or auditors interested in finding (and exploiting) weak PRNGs.
- Students seeking to learn about Computer Science, applied mathematics, or cybersecurity.
- Educators seeking to teach about PRNGs
  
## Contents
| Section | Description |
|---------|-------------|
| [Paper](./Cracking-Chaos-Making-Using-and-Breaking-PRNGs.pdf) | Full paper (14 pages) |
| BBS.py | Implements Blum-Blum-Shub-4096 from scratch, including prime generation via Miller-Rabin testing. |
| ChaCha20.py | Implements Bernstein's original ChaCha20 variant. |
| CTRMag.py | Implements the Soviet Magma block cipher in CTR mode. |
| DUAL_EC.py | Implements DUAL_EC_DRBG on M-383, showcasing the backdoor and using it to recover state. |
| HashDRBG.py | Implements a simplified variant of NIST's Hash_DRBG using SHA256. |
| LCG.py | Implements ranqd1 from numerical recipes, and fully recovers it via Marsaglia's Theorem. Also visualizes Marsaglia's Theorem in 3D. |
| LFSR.py | Implements an 8 bit Linear Feedback Shift Register, and shows inversion of it via Berlekamp-Massey. |
| MT19937.py | Implements MT19937, the most common variant of the Mersenne Twister, and inverts it by inverse tempering and state cloning. |
| Philox.py | Implements Philox4x32-10, the most common counter-based PRNG, in use by cuRAND, Intel, and C++26. |
| RC4.py | Implements RC4, and showcases detection via the second byte bias towards 0. |

## Further Reading and References
A full bibliography can be found within the [paper](./Cracking-Chaos-Making-Using-and-Breaking-PRNGs.pdf).
