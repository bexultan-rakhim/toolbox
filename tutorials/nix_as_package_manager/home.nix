# this is a template!
{ config, pkgs, ... }:

{
  home.username = "<your-username>"; # replace <your-username> with username in your system
  home.homeDirectory = "/home/<your-username>"; # replace <your-username> with username in your system. /User/<your-username> in macOS
  home.stateVersion = "25.11"; # this should be latest stable version

  home.packages = with pkgs; [
    htop # these are programs that will be installed by nix
    ripgrep
    bat
  ];

  programs.zsh = { # or replace with bash if you use bash
    enable = true;
    shellAliases = {
      hm-edit = "nvim ~/.config/home-manager/home.nix"; # help of use
     # Note the slightly different command for Flakes:
      hm-switch = "home-manager switch --flake ~/.config/home-manager#your-username";
    };
  };
}

