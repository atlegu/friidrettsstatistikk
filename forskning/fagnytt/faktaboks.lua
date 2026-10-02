-- Gjør ::: {.faktaboks} ... ::: om til et tcolorbox-miljø, men lar innholdet forbli markdown.
function Div(el)
  if el.classes:includes('faktaboks') then
    local blocks = { pandoc.RawBlock('latex', '\\begin{faktaboks}') }
    for _, b in ipairs(el.content) do table.insert(blocks, b) end
    table.insert(blocks, pandoc.RawBlock('latex', '\\end{faktaboks}'))
    return blocks
  end
end
