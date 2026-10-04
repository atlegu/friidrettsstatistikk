-- Pandoc-filter for Word-utgave av Fagnytt-artikler: layoutklasser blir vanlige avsnitt/overskrifter.
local function titled(title, el)
  local blocks = { pandoc.Header(3, title) }
  for _, b in ipairs(el.content) do table.insert(blocks, b) end
  return blocks
end
function Div(el)
  if el.classes:includes('sitat') then
    return pandoc.BlockQuote(el.content)
  elseif el.classes:includes('faktaboks') then
    return titled('Faktaboks: Slik er tallene laget', el)
  elseif el.classes:includes('raad') then
    return titled(el.attributes['tittel'] or 'Råd til treneren', el)
  elseif el.classes:includes('forfatter') then
    return titled('Om forfatteren', el)
  elseif el.classes:includes('boks') then
    return titled(el.attributes['tittel'] or '', el)
  elseif el.classes:includes('referanser') then
    return el.content
  end
end
