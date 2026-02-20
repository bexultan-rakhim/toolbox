package main

type GraphVizVisitor struct {
	contaier_level  bool
	graphStr        string
	knownSystems    map[string]bool
	knownContainers map[string]bool
}

func (v *GraphVizVisitor) visitLink(l *Link) {
	v.graphStr += l.Target + " [" + "label=" + `"` + l.Description
	if l.Kind == LKindAsync && l.Via != "" {
	  v.graphStr += "\\n via: [" + l.Via + "]"
	}
	v.graphStr += `"`
	v.graphStr += " arrowhead=open "
	if l.Kind != LKindSync {
	  v.graphStr += " style=dashed "
	}
	switch l.Status {
	case StatusPlanned:
	  v.graphStr +=" color=green"
	case StatusDeprecated:
	  v.graphStr +=" color=red"
	default:
	  // ignore
	}
	v.graphStr += "];\n" 
}

func (v *GraphVizVisitor) visitContainer(c *Container) {
	v.graphStr += "  " + c.ID + " [" + "label=" + `"` + c.Name + `"` 
	switch c.Kind {
	case CKindStorage:
		v.graphStr += " shape=cylinder"
	case CKindActor:
		v.graphStr += " shape=oval"
	default:
		v.graphStr += " shape=box"
	}
	switch c.Status {
	case StatusPlanned:
	  v.graphStr +=" color=green"
	case StatusDeprecated:
	  v.graphStr +=" color=red"
	default:
	  // ignore
	}
	v.graphStr += " ];\n"
}

func (v *GraphVizVisitor) visitSystemContLevel(s *System) {
	if s.External {
		v.graphStr += "  " + s.ID + " [" + "label=" + `"` + s.Name + `"` 
		switch s.Kind {
		case SKindActor:
			v.graphStr += " width=0.5 shape=oval"
		default:
			v.graphStr += " shape=box"
		}
		switch s.Status {
		case StatusPlanned:
		  v.graphStr +=" color=green"
		case StatusDeprecated:
		  v.graphStr +=" color=red"
		default:
		  // ignore
		}
		v.graphStr += " ];\n"
		for _, l := range s.Links {
			if v.knownContainers[l.Target] || v.knownSystems[l.Target] {
				v.graphStr += "  " + s.ID + " -> "
				l.accept(v)
			}
		}
		// no subgraph for external
		return
	}

	v.graphStr += "  subgraph cluster_" + s.ID + " {\n"
	v.graphStr += `    label="` + s.Name + `"` + ";\n"
	v.graphStr += `    style=dashed` + ";\n"
	for _, c := range s.Containers {
		v.graphStr += "  "
		c.accept(v)
	}
	v.graphStr += "  }\n"
	for _, c := range s.Containers {
	  for _, l := range c.Links {
	    v.graphStr += "  " + c.ID + " -> "
	    l.accept(v)
	  }
	}
}

func (v *GraphVizVisitor) visitSystemSysLevel(s *System) {
  v.graphStr += "  " + s.ID + " [" + "label=" + `"` + s.Name + `"` 
	switch s.Kind {
	case SKindActor:
		v.graphStr += " width=0.5 shape=oval"
	default:
		v.graphStr += " shape=box"
	}
	switch s.Status {
	case StatusPlanned:
	  v.graphStr +=" color=green"
	case StatusDeprecated:
	  v.graphStr +=" color=red"
	default:
	  // ignore
	}
	v.graphStr += " ];\n"
  for _, l := range s.Links {
	if !v.knownSystems[l.Target] { return }
	v.graphStr += "  " + s.ID + " -> "
	l.accept(v)
  }
}

func (v *GraphVizVisitor) visitSystem(s *System) {
	if !v.contaier_level {
	  v.visitSystemSysLevel(s)
	} else{
	  v.visitSystemContLevel(s)
	}
}

func (v *GraphVizVisitor) visitImport(i *Import) {
	// TODO: add external imports maybe...
	// ignore...
}

func (v *GraphVizVisitor) visitRoot(r *Root) {
	v.graphStr += "  graph[\n"
	v.graphStr += `    label="` + r.Context + `"` + "\n"
	v.graphStr += "  ];\n"

	v.knownSystems = make(map[string]bool)
	if r.System != nil {
		v.knownSystems[r.System.ID] = !v.contaier_level ||  r.System.External
		r.System.accept(v)
		if !v.knownSystems[r.System.ID]{
			v.knownContainers = make(map[string]bool)
			for _, c := range r.System.Containers {
				v.knownContainers[c.ID] = true
			}
		}
		return
	}
	
	for _, s :=range r.Systems {
		v.knownSystems[s.ID] = !v.contaier_level || s.External
		if !v.knownSystems[s.ID] {
			v.knownContainers = make(map[string]bool)
			for _, c := range s.Containers {
				v.knownContainers[c.ID] = true
			}
		}
	}

	for _, s := range r.Systems {
		s.accept(v)
	}
}

func (g *GraphVizVisitor) generateGraphviz(r Root) (string, error) {
	g.graphStr += "digraph G{\n"
	g.graphStr += "  rankdir=TB;\n"
	g.graphStr += `  node [shape=box, style=filled, fontname="Arial"];` +"\n"
	g.graphStr += `  edge [labelforce=true];` + "\n"


	r.accept(g)

	g.graphStr += "}\n"
	return g.graphStr, nil
}
