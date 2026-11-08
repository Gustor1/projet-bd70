"""Export the relational SVG layout as editable diagrams.net tables and connectors."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

base = Path(__file__).resolve().parents[1]
svg = ET.parse(base / "docs/diagrammes/mld-complet.svg").getroot()
ns = "{http://www.w3.org/2000/svg}"
width, height = map(float, svg.get("viewBox").split()[2:])
graph = svg.find(ns + "g")
dx, dy = map(float, re.search(r"translate\(([^)]+)\)", graph.get("transform")).group(1).split())
file = ET.Element("mxfile", host="app.diagrams.net")
page = ET.SubElement(file, "diagram", name="Schéma relationnel")
model = ET.SubElement(page, "mxGraphModel", pageWidth=str(width), pageHeight=str(height))
root = ET.SubElement(model, "root")
ET.SubElement(root, "mxCell", id="0")
ET.SubElement(root, "mxCell", id="1", parent="0")

def vertex(key, parent, value, style, x, y, w, h):
    cell = ET.SubElement(root, "mxCell", id=key, parent=parent, value=value, style=style, vertex="1")
    ET.SubElement(cell, "mxGeometry", attrib={"as":"geometry", "x":str(x), "y":str(y), "width":str(w), "height":str(h)})

def pairs(text):
    nums = list(map(float,re.findall(r"-?\d+(?:\.\d+)?",text)))
    return list(zip(nums[::2],nums[1::2]))

bounds = {}
for node in graph.findall(ns+"g"):
    if node.get("class") != "node":
        continue
    name = node.findtext(ns+"title")
    points = [p for poly in node.findall(ns+"polygon") for p in pairs(poly.get("points"))]
    xs,ys = zip(*points)
    x,y,w,h = min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)
    bounds[name] = (x,y,w,h)
    vertex(name,"1","","container=1;recursiveResize=0;fillColor=#ffffff;strokeColor=#8fa8be;",x+dx,y+dy,w,h)
    for i,t in enumerate(node.findall(ns+"text")):
        title=i==0
        style="text;align=left;verticalAlign=middle;spacing=0;strokeColor=none;fontFamily=Arial;fontSize=12;"
        tx = 0 if title else float(t.get("x"))-x
        if title:
            style += "align=center;fontStyle=1;fillColor=#17324d;fontColor=#ffffff;"
        vertex(name+"-label-"+str(i),name,t.text or "",style,tx,float(t.get("y"))-y-15,w-tx,20)

for group in graph.findall(ns+"g"):
    if group.get("class") != "edge":
        continue
    source,target = group.findtext(ns+"title").split("->")
    labels = group.findall(ns+"text")
    pts=pairs(group.find(ns+"path").get("d"))
    style="endArrow=block;strokeColor=#617b94;fontSize=10;labelBackgroundColor=#ffffff;"
    for key,table,point in [('exit',source,pts[0]),('entry',target,pts[-1])]:
        x,y,w,h=bounds[table]
        style+=f"{key}X={max(0,min(1,(point[0]-x)/w))};{key}Y={max(0,min(1,(point[1]-y)/h))};"
    edge=ET.SubElement(root,"mxCell",id=group.get("id"),parent="1",edge="1",source=source,target=target,value=labels[0].text,style=style)
    geo=ET.SubElement(edge,"mxGeometry",attrib={"as":"geometry","relative":"1"})
    arr=ET.SubElement(geo,"Array",attrib={"as":"points"})
    for px,py in pts[1:-1]:
        ET.SubElement(arr,"mxPoint",x=str(px+dx),y=str(py+dy))
    for idx,(label,pos) in enumerate(zip(labels[1:],["0.85","-0.85"])):
        child=ET.SubElement(root,"mxCell",id=group.get("id")+"-card"+str(idx),parent=edge.get("id"),value=label.text,vertex="1",connectable="0",style="edgeLabel;align=center;verticalAlign=middle;labelBackgroundColor=#ffffff;fontSize=10;")
        ET.SubElement(child,"mxGeometry",attrib={"as":"geometry","relative":"1","x":pos,"y":"10"})
out=base/"livrables/schema-relationnel/mld-complet.drawio"
ET.indent(file)
ET.ElementTree(file).write(out,encoding="utf-8",xml_declaration=True)
