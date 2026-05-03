# Visual Hooks for AI Hook-Scene Generation

Direction reference for prompting hook scenes (Veo / Runway / Sora / etc.) for
30–60s direct-response ads. Synthesized from:

- `dNT7gd3ulAg` — Jade Beason, *I studied 100+ hooks*
- `2byPP_9F0-Q` — Kallaway, *Give me 15 mins, I'll make your hooks impossible to skip*
- `ImzoNTrgvFg` — Kallaway, *The NEW Way to WIN on Social Media in 2026*
- `GsfbnzN77NY` — Ryan Spenner, *5 Viral Storytelling Hooks Pt. 4*
- `xbi3CKpvUAI` — Ryan Spenner, *5 Visual Hooks Pt. 7*

Companion to [`dr-ad-script-frameworks.md`](./dr-ad-script-frameworks.md).

---

## 1. The frame shift: hook is a moment, not a sentence

The single biggest update from these videos. The old approach treated the hook
as a verbal opener — one catchy line. The new approach treats it as a
**designed moment** built from three elements that have to be prompted together:

1. **Words** — what's said in the first 1–3 seconds.
2. **Visuals** — what's on screen, including motion, props, captions, effects.
3. **Pacing** — how fast everything moves. Energy, cuts, dead air.

For an AI generator, this means a hook scene prompt that only specifies dialogue
will produce a flat scene. Prompt all three layers explicitly.

---

## 2. Hook's two and only jobs (Kallaway)

A hook needs to give the viewer two things — nothing more:

1. **Topic clarity** — they understand what the next 30–60s is about.
2. **On-target curiosity** — they believe the value is for them.

Everything in this doc is in service of those two outcomes. If a generated hook
fails one of them, it's broken regardless of how cool it looks.

---

## 3. The Four Horsemen — diagnostic for failing hooks (Kallaway)

When a generated hook isn't working, run it through this checklist before
regenerating:

| # | Mistake | Symptom | Fix |
|---|---|---|---|
| 1 | **Delay** | Topic isn't introduced until line 3+ | Move topic into seconds 1–2 ("speed-to-value") |
| 2 | **Confusion** | Sentence is grammatically dense or jargon-heavy | Rewrite at 6th-grade reading level, active voice, fewer words |
| 3 | **Irrelevance** | Sounds like it's about the creator, not the viewer | Swap "I/me" for "you/your"; agitate a known painpoint |
| 4 | **Disinterest** | Clear and relevant but boring | Add **contrast** (see §4 below) |

Most "this hook is mid" feedback is one of these four. Name the failure mode
before iterating.

---

## 4. Curiosity = Contrast (Kallaway)

Curiosity loops are not magic — they're contrast. The engine:

> **Compare A (what the viewer already believes) with B (your contrarian
> alternative).** The distance between A and B is the curiosity.

Two ways to express it in a hook:

- **Stated contrast** — both A and B verbal: *"Most people solve acne with Accutane, but I have an herbal remedy that works 3× faster."*
- **Implied contrast** — only B is verbal; A is what the viewer assumes: *"This herbal supplement is 8× more effective for acne."* (Accutane / nothing is the implied A.)

For DR ads, **stated** is safer because the audience may not share the implied
baseline. Use implied only when you're sure the painpoint and existing solutions
are universally known in the niche.

This is the same principle behind the **Named Villain** archetype in our DR
beat sheet — naming the villain *is* setting up the A vs B contrast.

---

## 5. Visual hook archetypes (scene-generation directions)

The catalog. Each entry is structured so you can paste it into a hook-scene
prompt with minor variable substitution.

### 5.1 Drop-in objects
**What:** Frame opens empty or sparse, then objects (boxes, props, the product) drop in from off-screen.
**Why it works:** Vertical motion on a still feed = pattern interrupt. Reveal sequence creates micro-curiosity ("what's in the box?").
**Prompt direction:** *"Static medium shot of [setting]. At t=0.3s, three [boxes / product cartons / items] drop from above and land in frame with a soft thud. Camera doesn't move."*

### 5.2 Screenwriting / typed-text on screen
**What:** Words appear as if being typed in real time, often word-by-word matching VO.
**Why it works:** Forces dual-channel processing (read + listen) → engagement bump.
**Prompt direction:** *"Word-by-word kinetic typography overlay synced to VO. Each word pops in with a 1-frame scale-up, monospace font, white on dark blur."*
**Note:** This is the single highest-leverage visual move per Jade Beason — appears in nearly all top-performing creator hooks.

### 5.3 Tripping / stumbling transition
**What:** Talent trips, drops something, or visibly stumbles in the first second, often paired with reactive dialogue ("oh ___").
**Why it works:** Pattern interrupt + relatable mess + implies story coming.
**Prompt direction:** *"Talent walks into frame, deliberately stumbles on [prop], catches themselves, reacts with surprised half-laugh. Hard cut to talking head."*

### 5.4 Foreshadow open (cold-open the consequence)
**What:** First 1–2 seconds show the dramatic outcome (someone falling, crying, the product fully assembled, the before/after reveal). Rest of the video shows how we got there.
**Why it works:** The hook IS the climax. Built-in curiosity loop — viewer needs to keep watching to learn how this happened.
**Prompt direction:** *"Open with [end-state moment, e.g., the empty plate, the messy room, the perfectly styled hair]. Hold for 1.2s. Cut to caption: 'Here's how I got here.'"*

### 5.5 Wind / hair / fabric flow ("Gone with the Wind")
**What:** Sudden gust, hair tossing, fabric billowing — exaggerated cinematic moment.
**Why it works:** Movement + drama in a still environment. Reads as "premium" / "produced."
**Prompt direction:** *"Talent stands still in [environment]. Off-screen fan triggers a sudden gust — hair and clothing flow dramatically for 0.8s. Slow-mo at 1.5×."*

### 5.6 Aesthetic environment placement ("Selfie cafe")
**What:** Hook is delivered from a visually arresting location — busy cafe, neon-lit street, design-forward studio. The location is the hook.
**Why it works:** Background does the pattern-interrupt work; talent doesn't have to.
**Prompt direction:** *"Selfie POV in [aesthetic location with clear visual identity]. Background characters / motion in soft focus. Talent talks to camera."*
**DR caveat:** Location must read in 0.5s on a phone screen. Pick environments with one dominant visual signature.

### 5.7 Walk-toward-camera open (Jade Beason's go-to)
**What:** Talent walks toward the camera while delivering line 1. Movement = perceived energy.
**Why it works:** Killing dead air; implies "something's about to happen"; matches scrolling-thumb kinetic energy.
**Prompt direction:** *"Wide shot. Talent 4 feet from camera, walks confidently toward it as VO line 1 plays. Stops at medium close-up by end of line."*

### 5.8 Fast zoom on frame 1
**What:** Camera punches in (or talent pushes face toward lens) at start of hook, often paired with a sound effect.
**Why it works:** Forces eye-lock; mimics "wait, listen up" energy.
**Prompt direction:** *"Medium shot of talent. At t=0s, fast 0.4s zoom-in to extreme close-up timed to first stressed syllable. Whoosh SFX on cut."*

### 5.9 Snapshot / preview grid
**What:** Hook shows a 2×2 or 3×1 grid preview of what's coming in the rest of the ad — the before/after, the products, the steps.
**Why it works:** Lets the viewer "see the whole map" in 1s; rewards staying for the full reveal.
**Prompt direction:** *"At t=1s, screen splits into [N] thumbnails showing [outcomes / products / steps]. Each thumbnail bounces in with a 1-frame delay. Captions label each."*

### 5.10 Unique camera angle
**What:** Open from a deliberately unusual angle — overhead, low/floor, dutch tilt, behind-the-shoulder, in-fridge POV.
**Why it works:** Eye recognizes "this isn't a normal talking head" → pattern interrupt.
**Prompt direction:** *"Open with [angle — e.g., overhead bird's-eye / floor-level looking up / inside-the-fridge POV]. Hold 1s before cutting to standard angle."*

### 5.11 Visible reaction (someone else)
**What:** Frame opens on a character reacting to something off-screen — shocked face, eyes widening, jaw drop. Then reveal what they're reacting to.
**Why it works:** Faces with strong expressions trigger mirror-neuron attention.
**Prompt direction:** *"Tight close-up on [character]'s face mid-reaction (surprise / disgust / wonder). Hold 0.6s. Cut to reverse showing what they're looking at."*

### 5.12 Product-as-prop reveal
**What:** Product enters the hook as a physical object being interacted with — picked up, opened, sprayed, dropped — not as a beauty shot.
**Why it works:** Shows product in use within the first 2s; double-duty hook + demo.
**Prompt direction:** *"Talent's hand enters frame holding [product], performs [signature action — pour / squeeze / click / unbox] in one continuous motion. Sync action peak to VO emphasis."*

---

## 6. Verbal hook templates (slot-fill, from Spenner + Kallaway)

These are reusable openers. Each has a slot that gets filled with the offer
specifics. They pair well with the visual archetypes above.

| Template | Slot | Example | Notes |
|---|---|---|---|
| "Quick question from a [role]…" | role with authority | *"Quick question from a psychologist…"* | Borrows perceived expertise instantly |
| "I once read somewhere that [insight]" | counter-intuitive insight | *"I once read somewhere we should change our what-ifs to even-ifs"* | Implies research; soft-sells contrast |
| "You're X but you want to be Y" | current state vs aspirational | *"You're H&M but you want to be Zara"* | Pure stated contrast (Kallaway's A vs B) |
| "Somebody told me you were in need of [X]" | the prospect's known want | *"…in need of a rebrand"* | Direct relevance via "you" pronoun |
| "Give me [N] seconds and I will [verb] your [pain]" | time + verb + painpoint | *"Give me 30 seconds and I will delete your self-doubt"* | Specific time = perceived contract |
| "If you've [pain], [contrarian solution]" | pain + B-side | *"If you've struggled with acne, this 45-min remedy has zero side effects."* | Kallaway-canonical structure |
| "Most people think X. The truth is Y." | belief vs reveal | *"Most people think cold email is dead. It's not — Google changed one rule."* | Stated contrast |
| "Stop [common action]. Start [contrarian action]." | habit swap | *"Stop counting calories. Start counting protein."* | Imperative + contrast |

**Pronoun rule (Kallaway):** Lead with **you / your**, not I / my. Even when
the line is technically about you, frame it through their experience.

---

## 7. Pacing rules for the first 3 seconds

From Jade Beason + Kallaway:

- **Topic must be clear by second 2.** Not "something crazy happened" — the
  actual topic. Speed-to-value.
- **No millennial pause.** Cut the dead air at the very start (the breath / the
  setup beat). Talent should already be talking when frame 1 plays.
- **Pauses only for drama.** A pause works *after* a curiosity-loaded line, not
  before one. *"I cried over social media this morning. … Embarrassing, I know."*
- **Energy match.** Talent's vocal energy should match the cadence of feed
  scrolling — slightly faster than conversational.
- **Hook is 2–3 lines, not 1.** Line 1 = topic clarity. Lines 2–3 = contrast /
  curiosity. Don't try to cram both into one line unless the line is unusually
  tight.

---

## 8. End-to-end direction prompt (template)

A working prompt for an AI scene generator that bakes all of the above in:

```
Generate a [duration]s vertical 9:16 hook scene.

VISUAL ARCHETYPE: [pick one from §5, e.g. "drop-in objects + walk-toward-camera"]
LOCATION: [brief setting description, max 8 words]
TALENT: [age, vibe, wardrobe in 1 line]

HOOK SCRIPT (2-3 lines, total ≤6s VO):
Line 1 (topic clarity, you/your, 6th-grade reading level):
  "[fill in]"
Line 2 (contrast — A vs B):
  "[fill in]"
Line 3 (optional — open the loop to the offer):
  "[fill in]"

PACING:
- VO starts on frame 1. No silent breath.
- [N] cuts in the first 3s.
- Talent energy: 1.1× conversational.

ON-SCREEN TEXT:
- Word-by-word kinetic captions synced to VO.
- Highlight the contrast keyword in [color].

SOUND:
- [whoosh / impact / silence] on the cut into the contrast line.

EXCLUDE:
- No millennial pause.
- No generic stat lead ("Did you know X% of…") unless the stat is jarring AND specific to the audience.
- No "I/me" framing in line 1.
```

---

## 9. Pre-flight checklist for a generated hook scene

Run before shipping any AI-generated hook to test:

- [ ] Topic is clear by second 2. (Mute the audio — does the visual + text alone tell me what this ad is about?)
- [ ] Hook reads at ≤6th-grade level. Run through a readability checker.
- [ ] Uses "you / your" at least once in lines 1–2.
- [ ] Has an A vs B contrast — stated or clearly implied.
- [ ] Visual archetype is one of the §5 list (or a defensible new one), not a generic talking head.
- [ ] No dead air / breath before the first word.
- [ ] At least one of: kinetic captions, motion, prop interaction, environment with strong visual identity.
- [ ] Three takes / variants generated, best one selected. (Jade's "third take is usually best" rule — for AI: generate 3 variants per hook, A/B them.)
- [ ] On a phone screen with sound off, the hook still works. (DR ads on Meta default to muted.)
- [ ] Hook can survive the Four Horsemen diagnostic — no delay, no confusion, no irrelevance, no disinterest.

---

## 10. What NOT to do (anti-patterns from these videos)

- **Generic stat leads.** *"80% of adults consume content across multiple formats…"* (Jade's failed-hook example.) Stat works only if it's jarring AND audience-specific.
- **Vague mystery hooks.** *"This is one of the craziest things I've ever seen."* (Kallaway's bad example.) Zero topic clarity → hard bounce.
- **Dense / passive sentences.** *"The online money they made is most difficult to earn if you don't develop a journaling practice."* (Kallaway's confusion example.) Rewrite to active voice + 6th-grade reading.
- **First-person framing.** *"I've struggled with skin problems my whole life."* → *"If you've struggled with skin problems…"*
- **Repurposed long-form snippet as a hook.** Per Jade — almost never works because the original wasn't designed to open cold.
- **Fast-cut overstimulation as a substitute for storytelling.** Per Kallaway's social-shifts video — this worked in 2022–2024 but is losing to intentional/cinematic now, especially for premium DTC brands.

---

## 11. Open extensions

- **Visual hook bank from competitor ads.** Same approach as the verbal hook stat library — use Upspring (or scraped TikTok / Meta ads) to populate a tagged library of working visual archetypes per vertical.
- **Per-vertical archetype heatmaps.** Some archetypes will dominate by vertical (e.g., aesthetic environment for skincare; product-as-prop for kitchen tools). Worth tracking which archetypes correlate with high ROAS in our own data.
- **Generation-tool-specific prompt presets.** §8's template is generator-agnostic. We should fork it per tool (Veo / Runway / Sora) once we know which produces the best output for which archetype.
