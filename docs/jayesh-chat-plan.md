# Jayesh: Slack and Discord plan

Goal: creator ek line chat app me bheje, team wahin chale, final render wahin dikhe.
Deadline: 16:00 IST tak ek app working. Demo recording 20:00 IST pe hai.

## Pehle yeh samjho

- Pehle sirf ek app poora karo. Doosra tabhi jab pehla pass ho jaye. Slack se shuru karo, kyunki Switch me Slack ka alag renderer file hai aur Discord ka nahi. Dono ka real test abhi nahi hua.
- Do apps ek saath shayad nahi chalenge. Template ke agent names fixed hain aur Switch same name dobara nahi leta. Isliye ek server pe ek hi import.
- Template me ab `bridge` param hai. Import form me app ka display name do. Khali chhoda to server ka default app lagega.
- `directory` param ab form me poochha jata hai. Apne machine pe repo ka absolute path do.
- Agents rules wahi rahenge. Template me naye fields mat daalo, sirf woh jo Switch ke `docs/TEMPLATES.md` me hain.

## Steps

1. Latest `main` pull karo. Nishit ke fixes push hone ke baad hi shuru karo.
2. Switch Console me chat app set up karo. Bot token sirf Console me jayega, repo me kabhi nahi.
3. Console me apna account us app se link karo. `{$creator}` isi ke bina fail hota hai. Form khud link offer karta hai.
4. Purane `studio-*` agents delete karo, purana room archive karo.
5. `agents/studio.template.yaml` import karo, `bridge` me app ka naam daalo, room banao.
6. Neeche wale tests chalao aur har ek ka result likho.

## Tests

| # | Karo | Pass tab jab |
| --- | --- | --- |
| 1 | Kickoff dekho | Charon agents ek line me intro dein, room chat app me dikhe |
| 2 | Chat app ke mention picker se `@studio-director` likho, phir plain text me `@studio-director` likho | Dono se Director jaage. Agar ek hi kaam kare to likho kaunsa |
| 3 | Ask bhejo: `Driftnote Plus ke liye 30 second launch video banao` | Brief aaye, Quill aur Keeper chalein |
| 4 | Script me `[need: price]` aaye | Cut na chale. Director creator ko tag karke need puchhe, aur tag phone pe notification de |
| 5 | Reply karo `@studio-director price 5 dollars` (test value) | Answer Quill tak jaye, chain aage badhe |
| 6 | Render tak chalne do | Director MP4 path post kare, aur `reply @studio-director approve or your change` likhe |
| 7 | Reply karo `@studio-director approve` | Director likhe `Creator approved. Closed. Nothing published.` aur ruk jaye |
| 8 | Sab agents ka post count dekho | Koi agent ek handoff pe do baar na jaage |

## Nishit ko yeh wapas do

- Kaunsa app chala, aur test 1 se 8 ka result.
- Test 2 ka jawab. Yeh sabse important hai, kyunki poori handoff chain mention pe tiki hai.
- Test 8 me double wake hua ya nahi.
- Exact error text, agar kuch fail hua. Screenshot bhi chalega.
- MP4 size (`ls -lh renders/<slug>/`). `send_attachment` ki limit 20MB hai.

## Mat karo

- MP4 chat me bhejne ka kaam abhi mat jodo. Agents ka "never upload" rule abhi laga hai, aur uspe Nishit ka decision pending hai.
- Bot token, `credentials.json`, `.hyperframes/` ya MP4 commit mat karo.
- `hyperframes skills update` ya `npx skills add` mat chalao.
- Fail ho to 45 minute se zyada mat atko. Nishit ko batao, phir doosra app try karenge. Hackathon team chat maangta hai, isliye Console room pe fallback mat maano.
