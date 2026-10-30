-- tabletext.lua - table cells in the paragraph style "Table Text" (10 pt; defined in the reference
-- document by build_r1.py). pandoc keeps its own style for plain cell text, so cell text becomes a
-- paragraph inside a div that carries the style, and an empty cell an empty paragraph.
local function wrap(cell)
  local blocks = {}
  for _, b in ipairs(cell.contents) do
    table.insert(blocks, b.t == "Plain" and pandoc.Para(b.content) or b)
  end
  if #blocks == 0 then blocks = {pandoc.Para({pandoc.Str("")})} end   -- empty cells too (else Normal spacing)
  cell.contents = {pandoc.Div(blocks, {["custom-style"] = "Table Text"})}
end

function Table(t)
  for _, row in ipairs(t.head.rows) do for _, c in ipairs(row.cells) do wrap(c) end end
  for _, body in ipairs(t.bodies) do
    for _, row in ipairs(body.body) do for _, c in ipairs(row.cells) do wrap(c) end end
  end
  return t
end
