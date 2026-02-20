package main

import (
	"fmt"
	"regexp"
	"gopkg.in/yaml.v3"
)

var contextRegex = regexp.MustCompile("^[a-z][a-z0-9_]*$")

type Technology []string

func (t *Technology) UnmarshalYAML(value *yaml.Node) error {
	var single string
	if err := value.Decode(&single); err == nil {
		*t = []string{single}
		return nil
	}
	var multi []string
	if err := value.Decode(&multi); err == nil {
		*t = multi
		return nil
	}
	return fmt.Errorf("technology must be string or []string")
}

type Status string
const (
	StatusActive     Status = "active"
	StatusPlanned    Status = "planned"
	StatusDeprecated Status = "deprecated"
)
func (s *Status) UnmarshalYAML(value *yaml.Node) error {
	var val string
	if err := value.Decode(&val); err != nil {
		return err
	}
	switch Status(val) {
		case StatusActive, StatusPlanned, StatusDeprecated:
			*s = Status(val)
			return nil
		default:
			return fmt.Errorf("invalid status: %s", val)
	}
}

type LinkKind string
const (
	LKindSync     LinkKind = "sync"
	LKindAsync    LinkKind = "async"

)
func (k *LinkKind) UnmarshalYAML(value *yaml.Node) error {
	var val string
	if err := value.Decode(&val); err != nil {
		return err
	}
	switch LinkKind(val) {
		case LKindSync, LKindAsync:
			*k = LinkKind(val)
			return nil
		default:
			return fmt.Errorf("invalid kind: %s", val)
	}
}
type ContainerKind string
const (
	CKindService ContainerKind = "service"
	CKindStorage ContainerKind = "storage"
	CKindQueue   ContainerKind = "queue"
	CKindActor   ContainerKind = "actor"

)
func (k *ContainerKind) UnmarshalYAML(value *yaml.Node) error {
	var val string
	if err := value.Decode(&val); err != nil {
		return err
	}
	switch ContainerKind(val) {
		case CKindService, CKindStorage, CKindQueue, CKindActor:
			*k = ContainerKind(val)
			return nil
		default:
			return fmt.Errorf("invalid kind: %s", val)
	}
}


type SystemKind string
const (
	SKindSystem SystemKind = "system"
	SKindActor  SystemKind = "actor"
)
func (k *SystemKind) UnmarshalYAML(value *yaml.Node) error {
	var val string
	if err := value.Decode(&val); err != nil {
		return err
	}
	switch SystemKind(val) {
		case SKindActor, SKindSystem:
			*k = SystemKind(val)
			return nil
		default:
			return fmt.Errorf("invalid kind: %s", val)
	}
}


type Attributes map[string]any;

type Link struct {
	Target      string     `yaml:"target"`
	Kind        LinkKind   `yaml:"kind,omitempty"`             // sync, async
	Status      Status     `yaml:"status,omitempty"` // active, planned, deprecated
	Attribute   Attributes `yaml:"attribute,omitempty"`
	Technology  Technology `yaml:"technology,omitempty"`
	Description string     `yaml:"description,omitempty"`
	Via         string     `yaml:"via,omitempty"` // not required if Kind is sync
}

type Container struct {
	ID          string        `yaml:"id"`
	Name        string        `yaml:"name"`
	Kind        ContainerKind `yaml:"kind"` // service, storage, queue, actor
	Status      Status        `yaml:"status,omitempty"`
	Attributes  Attributes    `yaml:"attributes,omitempty"`
	Technology  Technology    `yaml:"technology,omitempty"`
	Description string        `yaml:"description,omitempty"`
	Links       []Link        `yaml:"links,omitempty"`
}

type System struct {
	ID          string      `yaml:"id"`
	Name        string      `yaml:"name"`
	Kind        SystemKind  `yaml:"kind,omitempty"` // actor, system
	Status      Status      `yaml:"status,omitempty"`
	Attributes  Attributes  `yaml:"attributes,omitempty"`
	Description string      `yaml:"description,omitempty"`
	External    bool        `yaml:"external,omitempty"`
	Technology  Technology  `yaml:"technology,omitempty"`
	Containers  []Container `yaml:"containers,omitempty"`
	Links       []Link      `yaml:"links,omitempty"`
}

type Import struct {
	Name string `yaml:"name"`
	From string `yaml:"from"`
	As   string `yaml:"as,omitempty"`
}

type Root struct {
	Context string   `yaml:"context"`
	Imports []Import `yaml:"imports,omitempty"`
	System  *System  `yaml:"system,omitempty"`
	Systems []System `yaml:"systems,omitempty"`
}

func (r *Root) Validate() error {
	if !contextRegex.MatchString(r.Context) {
		return fmt.Errorf("context '%s' must match ^[a-z][a-z0-9_]*$", r.Context)
	}
	hasSingle := r.System != nil
	hasMulti := len(r.Systems) > 0
	if (hasSingle && hasMulti) || (!hasSingle && !hasMulti) {
		return fmt.Errorf("must provide exactly one of 'system' or 'systems'")
	}

	knownIDs := make(map[string]bool)

	for _, imp := range r.Imports {
		id := imp.Name
		if imp.As != "" {
			id = imp.As
		}
		knownIDs[id] = true
	}

	var allSystems []System
	if hasSingle {
		allSystems = append(allSystems, *r.System)
	} else {
		allSystems = r.Systems
	}

	for _, s := range allSystems {
		if s.External && len(s.Containers) > 0 {
			return fmt.Errorf("External systems should not define containers! '%s' contains containers!", s.ID)
		} 
		knownIDs[s.ID] = true
		for _, c :=range s.Containers {
			knownIDs[c.ID] = true
		}
	}

	for _, s := range allSystems {
		if err := validateLinks(s.Links, s.ID, knownIDs); err != nil {
			return err
		}
		for _, c := range s.Containers {
			if err := validateLinks(c.Links, c.ID, knownIDs); err != nil {
				return err
			}
		}
	}

	return nil
}

func validateLinks(links []Link, parentID string, knownIDs map[string]bool) error {
	for _, l := range links {
		if !knownIDs[l.Target] {
			return fmt.Errorf("invalid link in '%s' target '%s' is unknown", parentID, l.Target)
		}
		if l.Kind == LKindSync && l.Via != "" {
			return fmt.Errorf("link in '%s' to '%s': 'via' is not required for sync links", parentID, l.Target)
		}
	}
	return nil
}


type Visitor interface {
	visitRoot(*Root)
	visitImport(*Import)
	visitSystem(*System)
	visitContainer(*Container)
	visitLink(*Link)
}

func (p *Root) accept(v Visitor) {
	v.visitRoot(p)
}
func (p *Import) accept(v Visitor) {
	v.visitImport(p)
}
func (p *System) accept(v Visitor) {
	v.visitSystem(p)
}
func (p *Container) accept(v Visitor) {
	v.visitContainer(p)
}
func (p *Link) accept(v Visitor) {
	v.visitLink(p)
}
