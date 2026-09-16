# Speculative Decoding LLM Speedup Simulation

This example simulates speculative decoding for Large Language Models (LLMs). It compares a traditional autoregressive generation process with a speculative one. The simulation uses a 'fast draft model' to propose multiple tokens and a 'slow verifier model' to check them, demonstrating how speculative decoding can significantly reduce inference latency when the draft model is accurate.

## Language

`python`

## How to Run

Save the code as `main.py` and run from your terminal: `python main.py`

## Original Article

This example accompanies the Turkish article: [Spekülatif Kod Çözme 2026: EAGLE, DFlash ve XPress ile Mühendisin Tam Kılavuzu](https://fatihsoysal.com/blog/spekulatif-kod-cozme-2026-eagle-dflash-ve-xpress-ile-muhendisin-tam-kilavuzu/).

## License

MIT — see [LICENSE](LICENSE).
