"""Denna filen är för att testa LLM's svar med logfilen"""

def search_in_log(logfil, sök_ord):
    try:
        with open(logfil, 'r') as file:
            for line in file:
                if line.find(sök_ord) != -1:
                    return True, line.strip()
        return False, None
    except FileNotFoundError:
        print(f"Error: FILEN '{logfil}' FINNS JU F*N INTE!!.")
        return False, None
    except Exception as e:
        print(f"Något konstigt skit hände: {e}")
        return False, None

# Exempel på användning
if __name__ == "__main__":
    logfil = "NÅGONTING.log"  # Namn på loggfilen
    sök_ord = "ERROR"    # Sökterm att leta efter

    found, match = search_in_log(logfil, sök_ord)
    if found:
        print(f"HITTADEEEEEEEEEEEEEE: {match}")
    else:
        print(f"HITTADE INGET FÖR: '{sök_ord}' i {logfil}.")
