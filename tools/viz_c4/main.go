package main

import (
	"fmt"
	"html/template"
	"io/ioutil"
	"log"
	"os"

	"gopkg.in/yaml.v3"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run main.go <path-to-yaml>")
		os.Exit(1)
	}

	data, err := ioutil.ReadFile(os.Args[1])
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	var root Root
	if err := yaml.Unmarshal(data, &root); err != nil {
		log.Fatalf("YAML Parsing Error: %v", err)
	}

	gDisabled := GraphVizVisitor{contaier_level: false}
	dotSys, _ := gDisabled.generateGraphviz(root)

	gEnabled := GraphVizVisitor{contaier_level: true}
	dotContainer, _ := gEnabled.generateGraphviz(root)

	const htmlTemplate = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Graphviz Toggle</title>
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script src="https://cdn.jsdelivr.net/npm/@hpcc-js/wasm@2.20.0/dist/graphviz.umd.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/d3-graphviz@5.6.0/build/d3-graphviz.js"></script>
    <style>#graph { cursor: pointer; }</style>
</head>
<body>
    <div id="graph" style="text-align: center;"></div>
    <script>
        const dotOff = {{.DotSys}};
        const dotOn = {{.DotCont}};
        let isEnabled = false;

        const graphviz = d3.select("#graph")
			.graphviz()
			.fit(true)
			.width(window.innerWidth)
			.height(window.innerHeight)
			.zoom(true);

        function render() {
            graphviz.renderDot(isEnabled ? dotOn : dotOff);
        }

        // Toggle on click
        d3.select("#graph").on("click", () => {
            isEnabled = !isEnabled;
            render();
        });

        render();
    </script>
</body>
</html>`

	page := map[string]interface{}{
		"DotSys": template.JS("`" + dotSys + "`"),
		"DotCont":  template.JS("`" + dotContainer + "`"),
	}

	f, _ := os.Create("index2.html")
	defer f.Close()
	tmpl := template.Must(template.New("viz").Parse(htmlTemplate))
	tmpl.Execute(f, page)
	fmt.Println(" Generated index2.html. Click the diagram to toggle containers.")
}
