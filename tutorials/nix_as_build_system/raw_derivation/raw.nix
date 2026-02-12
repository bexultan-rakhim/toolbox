derivation {
  name = "raw-hello";
  system = "x86_64-linux"; # Use builtins.currentSystem in real scripts
  builder = "/bin/sh";     # Use a hardcoded path to a shell
  args = [ 
    "-c" 
    "echo 'Raw Nix Build' > $out" 
  ];
}
