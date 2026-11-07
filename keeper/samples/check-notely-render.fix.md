```
BRAND CHECK | render | Notely launch video
Verdict: FIX
Issues:
1. 3.3s to 22s, problem and solution lists | Body lines are Space Grotesk 700 with line height 1.5 and 1.26, but only titles and hooks may use Space Grotesk, and everything else is Inter 400 at line height 1.5 | Set #problem-list and #solution-list to font-family Inter, font-weight 400, line-height 1.5, letter-spacing normal
2. 0s to 22s, tabs, scraps and Notely panel | Fill measures about #272A4E (source --panel #262B4D), which is not in the palette, and cards must be Paper | Set .tab, .scrap and #panel background to Paper #F4EFE6, and set the #panel h2 "Notely" color to Night navy #1B1F3B so it stays readable. Rows stay Night navy with Paper text
3. 10.2s to 22s, Notely panel | box-shadow darkens the navy around the panel to about #18193 3, but the finish must be flat colour on night navy | Remove box-shadow from #panel
4. 12.4s to 22s panel rows, and 23.1s to 30s URL | Inter is set to weight 500, but the rule is Inter 400 at line height 1.5 | Set .row and #cta-url to font-weight 400 and line-height 1.5, and load Inter wght@400 in the font link
Next: @studio-cut please re-render
```
