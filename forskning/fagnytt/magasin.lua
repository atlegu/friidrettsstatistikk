-- Pandoc-filter for magasinmalen (to spalter).
--   ![Figur 1. Tekst](fil.png)             -> figure* over hele bredden, "FIGUR 1" som etikett
--   ![...](fil.png){.smal}                 -> figure i spaltebredde
--   ::: {.sitat} ... :::                   -> uthevet sitat i spalten
--   ::: {.faktaboks} ... :::               -> faktaboks (spaltebredde, kan deles)
--   ::: {.raad} ... :::                    -> "Fem råd"-boks over hele bredden (figure*)
--   ::: {.forfatter} ... :::               -> forfatterboks
--   ::: {.referanser} ... :::              -> liten skrift med hengende innrykk

local function latex(s) return pandoc.RawBlock('latex', s) end

local function wrap(el, before, after)
  local blocks = { latex(before) }
  for _, b in ipairs(el.content) do table.insert(blocks, b) end
  table.insert(blocks, latex(after))
  return blocks
end

local function caption_latex(inlines)
  local txt = pandoc.utils.stringify(inlines)
  local label, rest = txt:match('^(Figur%s+%d+)%.%s*(.*)$')
  local doc = pandoc.Pandoc({ pandoc.Para(inlines) })
  local body = pandoc.write(doc, 'latex')
  body = body:gsub('\n$', '')
  if label then
    local rest_doc = pandoc.write(pandoc.Pandoc({ pandoc.Para(pandoc.Str(rest)) }), 'latex'):gsub('\n$', '')
    return '\\figlabel{' .. label:upper() .. '}' .. rest_doc
  end
  return body
end

function Figure(fig)
  local img
  for _, b in ipairs(fig.content) do
    if b.t == 'Plain' or b.t == 'Para' then
      for _, i in ipairs(b.content) do if i.t == 'Image' then img = i end end
    end
  end
  if not img then return nil end
  local cap = caption_latex(fig.caption.long and fig.caption.long[1] and fig.caption.long[1].content or {})
  local smal = img.classes:includes('smal')
  local env = smal and 'figure' or 'figure*'
  local width = smal and '\\linewidth' or '\\textwidth'
  return latex('\\begin{' .. env .. '}[t]\n\\centering\n' ..
    '\\includegraphics[width=' .. width .. ']{' .. img.src .. '}\n' ..
    '\\caption{' .. cap .. '}\n\\end{' .. env .. '}')
end

function Div(el)
  if el.classes:includes('sitat') then
    return wrap(el, '\\begin{sitat}', '\\end{sitat}')
  elseif el.classes:includes('faktaboks') then
    return wrap(el, '\\begin{figure*}[t]\n\\begin{faktaboks}\n\\begin{multicols}{2}', '\\end{multicols}\n\\end{faktaboks}\n\\end{figure*}')
  elseif el.classes:includes('raad') then
    return wrap(el, '\\begin{figure*}[t]\n\\begin{raadboks}\n\\begin{multicols}{2}', '\\end{multicols}\n\\end{raadboks}\n\\end{figure*}')
  elseif el.classes:includes('forfatter') then
    return wrap(el, '\\begin{forfatterboks}', '\\end{forfatterboks}')
  elseif el.classes:includes('referanser') then
    return wrap(el, '\\begin{referanser}', '\\end{referanser}')
  end
end
