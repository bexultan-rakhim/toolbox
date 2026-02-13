derivation {
  name = "hello";
  system = "aarch64-darwin"; # Use builtins.currentSystem in real scripts
  builder = "/bin/sh";     # Use a hardcoded path to a shell
  args = [ 
    "-c" 
    "echo 'Raw Nix Build' > $out" 
  ];
}
