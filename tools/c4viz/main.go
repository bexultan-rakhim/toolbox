package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"html/template"
	"gopkg.in/yaml.v3"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run main.go <path-to-yaml>")
		os.Exit(1)
	}

	filename := os.Args[1]

	data, err := ioutil.ReadFile(filename)
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	var root Root
	err = yaml.Unmarshal(data, &root)
	if err != nil {
		log.Fatalf("YAML Parsing Error:\n%v", err)
	}

	if err := root.Validate(); err != nil {
		log.Fatalf("Validation Error: %v", err)
	}

	fmt.Printf("✅ Successfully validated: %s (Context: %s)\n", filename, root.Context)

	grapviz, err := generateGraphviz(root)
	if err != nil {
		log.Fatalf("Failed to generate Graphviz:\n%v", err)
	}
	const htmlTemplate = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script src="https://cdn.jsdelivr.net/npm/@hpcc-js/wasm@2.20.0/dist/graphviz.umd.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/d3-graphviz@5.6.0/build/d3-graphviz.js"></script>
</head>
<body>
    <div id="graph" style="text-align: center;"></div>
    <script>
        const dotData = {{.DotString}};

        // Use the modern initialization pattern
        const graphviz = d3.select("#graph").graphviz();
        
        graphviz
            .fade(false)
            .renderDot(dotData);
    </script>
</body>
</html>`

	fmt.Printf("%s", grapviz)
	page := map[string]interface{}{
		"DotString": template.JS("`" + grapviz + "`"),
	}

	f, _ := os.Create("index.html")
	defer f.Close()

	tmpl := template.Must(template.New("viz").Parse(htmlTemplate))
	tmpl.Execute(f, page)

}
