package main

type GraphVizVisitor struct {
	contaier_level bool
	graphStr       string
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
	v.graphStr += "  " + c.ID + " [" + "label=" + `"` + c.Name + `"` + " shape=box];\n" 
	for _, l := range c.Links {
		v.graphStr += "  " + c.ID + " -> "
		l.accept(v)
	}

}

func (v *GraphVizVisitor) visitSystem(s *System) {
	if !v.contaier_level || s.External {
	  v.graphStr += "  " + s.ID + " [" + "label=" + `"` + s.Name + `"` + " shape=box];\n" 
	  for _, l := range s.Links {
		v.graphStr += "  " + s.ID + " -> "
		l.accept(v)
	  }
	  return
	}

	v.graphStr += "  subgraph " + s.ID + "{\n"
	for _, c := range s.Containers {
		v.graphStr += "  "
		c.accept(v)
	}
	v.graphStr += "  }\n"

		
}

func (v *GraphVizVisitor) visitImport(i *Import) {
	// TODO: add external imports
	// ignore...
}

func (v *GraphVizVisitor) visitRoot(r *Root) {
	v.graphStr += "  graph[\n"
	v.graphStr += `    label="` + r.Context + `"` + "\n"
	v.graphStr += "    labelloc=t\n"
	v.graphStr += "  ];\n"
	if r.System != nil {
		r.System.accept(v)
		return
	}

	for _, s := range r.Systems {
		s.accept(v)
	}
}

func (g *GraphVizVisitor) generateGraphviz(r Root) (string, error) {
	g.graphStr += "digraph G{\n"
	g.graphStr += "  rankdir=TB;\n"

	r.accept(g)

	g.graphStr += "}\n"
	return g.graphStr, nil
}
