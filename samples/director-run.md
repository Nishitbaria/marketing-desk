# Director walkthrough: Notely

DEMO / SYNTHETIC. These are expected messages, not a real run. Nothing here was rendered. The creator's answer, the script lines and the measurements only show the shape of each message.

Ask: make a 30s launch video for Notely

**1. Creator**

```
@studio-director make a 30s launch video for Notely
```

**2. Director asks one question.** Notely is not the product in `brand/brand.md`, so its facts must come from the creator.

```
What is Notely, and who is it for?
```

**3. Creator**

```
A notes app for indie devs.
```

**4. Director posts the brief and tags Quill**

```
BRIEF | Notely launch
Format: launch
Length: 30
Aspect: 9:16
Goal: Get indie devs to try Notely
Audience: Indie devs
Key message: Notely is a notes app for indie devs
@studio-quill write this
```

**5. Quill posts the script.** The six parts are shortened here.

```
**Format**: launch, 30s, 9:16, Shorts
...
**Open questions**: CTA link. What should the video say Notely does?
cc @studio-director
ready for @studio-keeper brand check
```

**6. Director reports**

```
script ✓ · brand checking…
```

**7. Keeper finds a problem**

```
BRAND CHECK | script | Notely launch
Verdict: FIX
Issues:
1. Full script | 84 spoken words, the limit for 30s is 70 | Cut the 14 words Keeper names in the beat at 10s
cc @studio-director
Next: @studio-quill please revise
```

**8. Director reports**

```
script ✓ · brand FIX 1 of 2 · revising…
```

**9. Quill reposts the full six parts**, with the same last two lines as step 5.

**10. Keeper passes the script**

```
BRAND CHECK | script | Notely launch
Verdict: PASS
Issues: None
cc @studio-director
Next: @studio-cut render it
```

**11. Director reports**

```
script ✓ · brand ✓ · rendering…
```

**12. Cut renders and posts**

```
renders/notely/notely.mp4
30.0s, 1080x1920, 9:16 (from ffprobe)
0-3s: hook text
3-10s: problem text
10-22s: solution text
22-30s: CTA with [need: CTA link]
cc @studio-director
@studio-keeper check render
```

**13. Director reports**

```
script ✓ · brand ✓ · render ✓ · final check…
```

**14. Keeper passes the render.** It is the only handoff with no `cc` line, because Next already tags Director.

```
BRAND CHECK | render | Notely launch
Verdict: PASS
Issues: None
Next: @studio-director approved render
```

**15. Director tags the creator**

```
@<creator> renders/notely/notely.mp4
approve or request changes
```

**16. Creator** approves or requests changes. Only the creator approves. No agent uploads, posts or publishes.

## If a stage keeps failing

The third FIX on the same piece stops the chain:

```
Next: @studio-director needs the creator's call
```

Director then tags the creator, lists the open issues and asks how to proceed.
