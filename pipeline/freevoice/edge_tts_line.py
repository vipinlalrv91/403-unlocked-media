"""Run with the viral-agent toolkit python: edge_tts_line.py <voice> <rate> <pitch> <out.mp3> < text"""
import asyncio, os, sys
import edge_tts
async def main(v, rate, pitch, out, text):
    c = edge_tts.Communicate(text, v, rate=rate, pitch=pitch, proxy=os.environ.get("HTTPS_PROXY") or None)
    await c.save(out)
asyncio.run(main(*sys.argv[1:5], sys.stdin.read().strip()))
