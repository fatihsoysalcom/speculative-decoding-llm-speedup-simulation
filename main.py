import time
import random

# --- Configuration ---
TARGET_SEQUENCE = "Hello, speculative decoding is fast!"
VERIFIER_TOKEN_DELAY = 0.1  # Simulate slow verifier model (e.g., large LLM)
DRAFTER_TOKEN_DELAY = 0.01   # Simulate fast draft model (e.g., small LLM)
DRAFTER_PROPOSAL_LENGTH = 5 # How many tokens the drafter proposes at once
DRAFTER_ACCURACY_RATE = 0.8 # Probability that a drafter's proposed token is correct

# --- Simulated Models ---

def slow_verifier_model(current_prefix: str) -> str:
    """
    Simulates a slow, highly accurate verifier LLM.
    It always produces the correct next token from the TARGET_SEQUENCE.
    """
    time.sleep(VERIFIER_TOKEN_DELAY)
    if len(current_prefix) < len(TARGET_SEQUENCE):
        return TARGET_SEQUENCE[len(current_prefix)]
    return "" # End of sequence

def fast_drafter_model(current_prefix: str, num_tokens: int) -> list[str]:
    """
    Simulates a fast, less accurate draft LLM.
    It proposes 'num_tokens' characters. It's mostly correct but can make errors.
    """
    proposed_tokens = []
    for i in range(num_tokens):
        time.sleep(DRAFTER_TOKEN_DELAY)
        if len(current_prefix) + i < len(TARGET_SEQUENCE):
            true_char = TARGET_SEQUENCE[len(current_prefix) + i]
            if random.random() < DRAFTER_ACCURACY_RATE:
                proposed_tokens.append(true_char)
            else:
                # Simulate an error: propose a random different character
                proposed_tokens.append(random.choice("abcdefghijklmnopqrstuvwxyz "))
        else:
            break # Reached end of target sequence
    return proposed_tokens

# --- Decoding Strategies ---

def autoregressive_decoding() -> tuple[str, float]:
    """
    Simulates traditional autoregressive decoding (verifier-only).
    Each token is generated sequentially by the slow verifier.
    """
    print("\n--- Starting Autoregressive Decoding ---")
    generated_text = ""
    start_time = time.perf_counter()

    while len(generated_text) < len(TARGET_SEQUENCE):
        # In autoregressive mode, the slow verifier generates one token at a time.
        next_token = slow_verifier_model(generated_text)
        if not next_token:
            break
        generated_text += next_token
        print(f"  [AR] Generated: '{generated_text[-1]}', Current: '{generated_text}'")

    end_time = time.perf_counter()
    duration = end_time - start_time
    return generated_text, duration

def speculative_decoding() -> tuple[str, float]:
    """
    Simulates speculative decoding.
    Uses a fast drafter to propose tokens, then a slow verifier to check them.
    """
    print("\n--- Starting Speculative Decoding ---")
    generated_text = ""
    start_time = time.perf_counter()

    while len(generated_text) < len(TARGET_SEQUENCE):
        # 1. Drafter proposes multiple tokens based on the current generated_text.
        proposed_tokens = fast_drafter_model(generated_text, DRAFTER_PROPOSAL_LENGTH)
        print(f"  [SD] Drafter proposed: '{''.join(proposed_tokens)}'")

        if not proposed_tokens and len(generated_text) < len(TARGET_SEQUENCE):
            # If drafter couldn't propose anything (e.g., near end), fall back to verifier.
            next_token = slow_verifier_model(generated_text)
            if not next_token:
                break
            generated_text += next_token
            print(f"  [SD] Drafter empty, verifier generated: '{next_token}', Current: '{generated_text}'")
            continue

        accepted_count = 0
        for i, proposed_token in enumerate(proposed_tokens):
            # 2. Verifier checks the proposed token. It effectively generates the true next token.
            # The prefix for the verifier includes already accepted tokens from this proposal.
            verifier_token = slow_verifier_model(generated_text + ''.join(proposed_tokens[:i]))

            if not verifier_token: # End of sequence
                break

            if proposed_token == verifier_token:
                # 3. If match, accept the token. This is the speedup: multiple tokens accepted at once.
                generated_text += proposed_token
                accepted_count += 1
                print(f"  [SD] Accepted: '{proposed_token}', Current: '{generated_text}'")
            else:
                # 4. If mismatch, accept previously correct tokens, then
                #    fall back to verifier for the current token and restart the process.
                print(f"  [SD] Mismatch at '{proposed_token}' (expected '{verifier_token}'). Fallback.")
                generated_text += verifier_token # Accept the correct token from verifier
                print(f"  [SD] Verifier corrected: '{verifier_token}', Current: '{generated_text}'")
                break # Break from checking proposed tokens and restart the while loop for new proposals.
        
        if accepted_count == len(proposed_tokens) and len(generated_text) < len(TARGET_SEQUENCE):
            print(f"  [SD] All {accepted_count} tokens accepted. Getting new proposals.")
        elif accepted_count < len(proposed_tokens) and accepted_count > 0:
            print(f"  [SD] Accepted {accepted_count} tokens before mismatch. Restarting proposal.")
        elif accepted_count == 0 and len(proposed_tokens) > 0:
             print(f"  [SD] No tokens accepted from this proposal. Restarting proposal.")

    end_time = time.perf_counter()
    duration = end_time - start_time
    return generated_text, duration

# --- Main Execution ---
if __name__ == "__main__":
    print(f"Target Sequence: '{TARGET_SEQUENCE}'")
    print(f"Verifier Delay: {VERIFIER_TOKEN_DELAY}s/token, Drafter Delay: {DRAFTER_TOKEN_DELAY}s/token")
    print(f"Drafter Proposal Length: {DRAFTER_PROPOSAL_LENGTH}, Drafter Accuracy: {DRAFTER_ACCURACY_RATE*100}%\n")

    # Run Autoregressive Decoding
    ar_text, ar_time = autoregressive_decoding()
    print(f"\nAutoregressive Result: '{ar_text}'")
    print(f"Autoregressive Time: {ar_time:.4f} seconds")

    # Run Speculative Decoding
    sd_text, sd_time = speculative_decoding()
    print(f"\nSpeculative Decoding Result: '{sd_text}'")
    print(f"Speculative Decoding Time: {sd_time:.4f} seconds")

    # Compare results
    print("\n--- Summary ---")
    print(f"Target: '{TARGET_SEQUENCE}'")
    print(f"Autoregressive: '{ar_text}' (Time: {ar_time:.4f}s)")
    print(f"Speculative:    '{sd_text}' (Time: {sd_time:.4f}s)")
    if sd_time < ar_time:
        print(f"Speculative decoding was {ar_time / sd_time:.2f}x faster!")
    else:
        print("Speculative decoding was not faster in this run (due to low accuracy or short sequence).")
