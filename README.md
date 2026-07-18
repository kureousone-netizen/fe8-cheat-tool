# FE8 Cheat Tool

A tool for bulk-editing unit stats, weapon levels, and items in **Fire Emblem: The Sacred Stones** by sending memory writes directly to mGBA via its Lua scripting API — no manual cheat code entry required.

## How It Works

1. Python reads the FE8 cheat code guide (PDF) and item data (CSV) to generate the correct memory addresses for whichever unit and stat/item you want to modify
2. Those addresses are sent over a local socket connection to a Lua script running inside mGBA
3. The Lua script writes the values directly to the game's memory in real time

## Setup

1. Extract this folder anywhere on your machine
2. Open `mGBA.exe` and load your FE8 ROM
3. **Start the game first** — the Lua script needs an active game session before it can run
4. Go to **Tools → Scripting → Load Script**, and select `client.lua`
5. Confirm the scripting console shows `mGBA socket server started on port 8888`

> ⚠️ **The order matters.** The game must already be running in mGBA *before* you load `client.lua`. Loading the script without a game running will cause it to fail silently.

## Usage

1. Run `fe8_cheat_writer.exe`
2. Follow the prompts to choose a unit, and the stat, weapon level, or item you want to set
3. The change applies immediately in-game — no need to open the cheats menu

## ⚠️ Known Limitation: Unit Slot Mapping

This tool reads cheat code data from a slot-based memory layout (Slot 1, Slot 2, Slot 3...), and **only slots 1 through 9 are guaranteed to map correctly** to your in-party unit order.

From slot 10 onward, the mapping can shift depending on:
- Which units have died or are otherwise missing from your active roster
- Which route you're on (Eirika's vs Ephraim's)
- How far into the game you are

This happens because units who are recruited but later lost (or never recruited on your route) still occupy a reserved slot in memory, silently shifting everyone after them.

**I attempted to account for this programmatically, but the number of branching variables (deaths, route choice, recruitment order) made a reliable fix impractical to test and maintain.** Rather than ship something that *looks* correct but silently writes to the wrong unit, this tool is scoped to units 1–9, where the mapping is consistent regardless of route or unit deaths.

**Recommendation:** Stick to modifying units 1–9. If you want to modify a unit beyond that range, you'll need to manually verify which slot number actually corresponds to them (e.g. by testing a small, reversible change like Max HP first and confirming in-game which unit it affected) before trusting the result.

## Folder Structure

```
mGBA-0.10.5-win64/
├── mGBA.exe                  # portable mGBA build (already present)
├── fe8_cheat_writer.exe       # this tool
├── scripts/
│   └── client.lua            # load manually in mGBA via Tools > Scripting
├── assets/
│   ├──  FE8 Cheat Guide.pdf
│   ├──  ItemForm_00809B10.csv
├── licenses/                 # mGBA's own files, unrelated to this tool
├── shaders/
└── README.md
```

## Troubleshooting

| Issue | Likely Cause |
|---|---|
| `ConnectionRefusedError` when running the exe | `client.lua` isn't loaded in mGBA, or it was loaded before the game started |
| Wrong unit's stats change | You're modifying a unit outside the 1–9 range — see the Known Limitation above |
| Game crashes after an edit | A multi-byte value (e.g. class) may have been written as a single byte — please file an issue with the unit/stat you were editing |

## Credits

Built using the [GameFAQs](https://gamefaqs.gamespot.com/gba/921183-fire-emblem-the-sacred-stones/faqs/36978) FE8 cheat code reference guide and item data exported from FEBuilderGBA.
