package main

import (
	"fmt"
	"html/template"
	"log"
	"os"
	"path/filepath"
	"gopkg.in/yaml.v3"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run main.go <path-to-yaml>")
		os.Exit(1)
	}

	data, err := os.ReadFile(os.Args[1])
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	exePath, err := os.Executable()
	if err != nil {
		log.Fatalf("Error - can not determine executable path")
	}

	exeDir := filepath.Dir(exePath)
	templatePath := filepath.Join(exeDir, "template", "index2.html")
	b, err := os.ReadFile(templatePath)
	if err != nil {
		log.Fatalf("Error reading template file: %v", err)
	}

	htmlTemplate := string(b) 

	var root Root
	if err := yaml.Unmarshal(data, &root); err != nil {
		log.Fatalf("YAML Parsing Error: %v", err)
	}

	gDisabled := GraphVizVisitor{contaier_level: false}
	dotSys, _ := gDisabled.generateGraphviz(root)

	gEnabled := GraphVizVisitor{contaier_level: true}
	dotContainer, _ := gEnabled.generateGraphviz(root)

	page := map[string]any {
		"DotSys": template.JS("`" + dotSys + "`"),
		"DotCont":  template.JS("`" + dotContainer + "`"),
	}

	f, _ := os.Create("index2.html")
	defer f.Close()
	tmpl := template.Must(template.New("viz").Parse(htmlTemplate))
	tmpl.Execute(f, page)
	fmt.Println(" Generated index2.html. Click the diagram to toggle containers.")
}
