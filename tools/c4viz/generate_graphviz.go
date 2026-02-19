package main

type GraphVizVisitor struct {
	graphStr string
}

func (v *GraphVizVisitor) visitLink(l *Link) {
	v.graphStr += l.Target + " [" + "label=" + `"` + l.Description + `"`
	v.graphStr += " arrowhead=open "
	if l.Kind != LKindSync {
	  v.graphStr += " style=dotted "
	}
	v.graphStr += "];\n" 
}

func (v *GraphVizVisitor) visitContainer(c *Container) {

}

func (v *GraphVizVisitor) visitSystem(s *System) {
	v.graphStr += "  " + s.ID + " [" + "label=" + `"` + s.Name + `"` + " shape=box];\n" 
}

func (v *GraphVizVisitor) visitImport(i *Import) {
}

func (v *GraphVizVisitor) visitRoot(r *Root) {
	v.graphStr += "  graph[\n"
	v.graphStr += `    label="` + r.Context + `"` + "\n"
	v.graphStr += "    labelloc=t\n"
	v.graphStr += "  ];\n"
}

func generateGraphviz(r Root) (string, error) {
	var g GraphVizVisitor
	g.graphStr += "digraph G{\n"
	g.graphStr += "  rankdir=TB;\n"
	r.accept(&g)
	for _, s := range r.Systems {
		s.accept(&g)
	}

	for _, s := range r.Systems {
		for _, l := range s.Links {
			g.graphStr += "  " + s.ID + " -> "
			l.accept(&g)
		}
	}

	g.graphStr += "}\n"
	return g.graphStr, nil
}
