{
  description = "VizC4 - cli tool to create static page for c4 models";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable"; # unstable Nixpkgs

  outputs =
    { self, ... }@inputs:

    let
      goVersion = 24; # Change this to update the whole stack

      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forEachSupportedSystem =
        f:
        inputs.nixpkgs.lib.genAttrs supportedSystems (
          system:
          f {
            pkgs = import inputs.nixpkgs {
              inherit system;
              overlays = [ inputs.self.overlays.default ];
            };
          }
        );
    in
    {
      overlays.default = final: prev: {
        go = final."go_1_${toString goVersion}";
      };

      packages = forEachSupportedSystem (
        { pkgs }:
        {
          default = pkgs.buildGoModule {
            pname = "vizc4";
            version = "0.1.0"; # Update this as your project evolves
            src = ./.;
            vendorHash = "sha256-g+yaVIx4jxpAQ/+WrGKxhVeliYx7nLQe/zsGpxV4Fn4=";
          };
        }
      );

      devShells = forEachSupportedSystem (
        { pkgs }:
        {
          default = pkgs.mkShellNoCC {
            packages = with pkgs; [
              go
              gotools
              golangci-lint
              gopls
            ];

            shellHook = ''
              export SHELL="${pkgs.bashInteractive}/bin/bash"
            '';
          };
        }
      );
    };
}
