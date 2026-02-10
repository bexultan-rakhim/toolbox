# Nix as Package Manager
## What
This is a brief tutorial on how to use Nix as a package manager.

## Why
As a developer, you have likely used several different operating systems. If you use macOS, you are familiar with homebrew. If you use Ubuntu, you know apt. (We do not talk about Windows—aka SlopOS, aka BloatOS).

Here are the main issues with these traditional package managers:

1.  **Imperative:** You install a version with brew install, which modifies your system in ways that may change things silently.
    
2.  **Version Conflicts:** You cannot easily have two versions of the same software at the same time (especially with FHS-compatible Linux systems). If you install program foo, it occupies /usr/bin/foo; you cannot have /usr/bin/foo-1.2 without jumping through hoops.
    
3.  **No Easy Rollback:** You usually just nuke the software, deal with the consequences, and manually fix the fallout.
    
4.  **Learning Curve & Fragmentation:** You have to learn both brew and apt, and you are limited by what is available in each. They often don't carry the same versions.
    
5.  **Portability:** Good luck recreating your exact environment when you get a new machine.

This tutorial explains how to use [nix](https://nixos.org/guides/how-nix-works/) as replacement for `homebrew` or `apt` for **user space** programs. 

>[!WARNING]
> This is a recipe tutorial. As such, I will not explain "how" `nix` works. You can learn more about `nix` here:
> 1. [How nix works](https://nixos.org/guides/how-nix-works/)
> 2. [Nix explained from the ground up](https://www.youtube.com/watch?v=5D3nUU1OVx8)
> 3. [Comma: Run software without installing](https://youtu.be/VUM3Km_4gUg?si=4rQMc_mTJQXgygUs)

## How
### 1. Installation
The cleanest way to install Nix is via the Determinate Installer, which handles the multi-user setup and systemd integration automatically. I recommend this way because it also installs nix with flakes and makes nix easy to remove (more info [here](https://zero-to-nix.com/)).
```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```
### 2. Setup
I will show setup using flakes and home manager. You can technically just setup home manager like this (next two steps work, but hold on for a sec before executing):

1. add the channel:
```bash
nix-channel --add https://github.com/nix-community/home-manager/archive/master.tar.gz home-manager
nix-channel --update
```
2. Install
```bash 
nix-shell '<home-manager>' -A install
```
This works. But, I like to have flake/home manager setup better, as it gives something important `flake.lock` file. This helps you to pin down exact versions and track the installed versions better. To do this, you can configure flake based setup manually.

1. Manually create a folder under `.config`:
```bash 
mkdir -p ~/.config/home-manager && cd ~/.config/home-manager
```
2. Create `flake.nix` (`touch flake.nix`)file inside this folder and put this as a content. Follow instructions in comments.
```nix
{
  description = "My Home Manager Flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { nixpkgs, home-manager, ... }:
    let
      system = "x86_64-linux"; # Use "aarch64-linux" for ARM, "x86_64-darwin" for Intel Mac, or "aarch64-darwin" for Apple Silicon (i.e. M1, M2, M3, M4 chips)
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      homeConfigurations."<your-username>" = home-manager.lib.homeManagerConfiguration { # replace <your-username> with username on your system
        inherit pkgs;
        modules = [ ./home.nix ]; # This points to your home.nix file that you will create in the next step
      };
    };
}
```
3. Create `home.nix` file and fill it with the following file, and follow instructions in the comments.
```nix
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
```
Save it and exit. You can find templates in this folder of the repo.
1. In the same folder run this command
```bash
nix run github:nix-community/home-manager -- switch --flake . -b backup
```
This command will bootstrap home manager (you are essentially running command that is located remotely!). If it succeeds, following happens:
1. You will have home manager installed (you can check with `home-manager --version`)
2. Nix will create `flake.lock` file (can check with `ls .` in the same folder where you have flake.nix file)
3. Installs software in the list (like htop) (you can check `htop --version`, `which htop`, that should point to `.nix-profile/bin/htop`)
4. Create new .bashrc file and copy the existing `.bashrc` to `.bashrc.backup` (you can check content of new `.bashrc`, now with bat `bat ~/.bashrc`)

### 3. Troubleshooting
### 1\. "Permission Denied" on /nix

If you didn't use the Determinate Installer, or if a previous install failed, you might not have permissions for the /nix directory.

*   **The Fix:** Nix requires a root-owned directory at /nix. If it exists and is broken, you may need to:sudo rm -rf /nix (Careful! This nukes all Nix data) and restart the installer.
    

### 2\. Command Not Found: nix or home-manager

If you just finished the install and your terminal doesn't recognize the commands:

*   **The Cause:** Your shell environment hasn't been updated to include the Nix binaries in your $PATH.
    
*   **The Fix:** Restart your terminal or run:. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
    

### 3\. Home Manager Conflict: "Existing file..."

When running hm-switch, you get an error: _“Existing file.../zshrc is in the way.”_

*   **The Cause:** Nix is protective. It won't overwrite your existing Ubuntu config files by force.
    
*   **The Fix:** Use the backup flag:home-manager switch --flake .#your-username -b backup
    

### 4\. GL and GUI App Crashes

If you install a GUI app (like alacritty or vlc) via Nix and it crashes on startup:

*   **The Cause:** Nix binaries can't find the OpenGL drivers on your Ubuntu host.
    
*   **The Fix:** You need **nixGL**.
    
    1.  Install it: nix profile install `github:guibou/nixGL --version-0-alpha`
        
    2.  Run your app through it: nixGL alacritty
        

### 5\. "Experimental Feature" Error

If you try to use Flakes and get an error about nix-command or flakes being disabled:

*   **The Fix:** Ensure your ~/.config/nix/nix.conf contains:
```
experimental-features = nix-command flakes
```

### 4. Pro Tips for Ease of Daily Use
You can now easily add new software by editing `home.nix` file using alias `hm-edit` feel free to change to any editor of your choice in `home.nix`! You just need to append new program in this list:
```nix
  home.packages = with pkgs; [
    htop
    ripgrep
    bat
    # put another program here!
  ];
```
You can find list of existing programs in Nix package store [here](https://search.nixos.org/packages).
After adding new program, to install it you just need to run `hm-switch` on your terminal. That is it!

Isn't it sweet? 

Also, you do not need to store your configs in `.config`. You can store it anywhere and just create a `symlink` there. Also, you can track these configs with `git`! Make sure to track `flake.lock` file as well! Also, feel free to adjust your workflow for your specific taste!

Also, now you can actually use nix to generate any configuration, similar to how you created `.bashrc` file! Learn more how to write modular flakes [here](https://www.youtube.com/watch?v=kvprcW6QMIE)

Some errors you may see when using nix:
1\. "File already exists" during hm-switch

The Error: Existing file '/home/user/.zshrc' is in the way of managed file... The Fix: This happens because Home Manager is too polite to delete your files. You must use the backup flag:
```bash
hm-switch -b backup
```
2\. "I'm out of Dis Space" Fix
Nix keeps every version of every package you've ever installed so you can roll back. If you don't clean it, /nix will eat your drive. Time to time, you want to run this:
```bash
# 1. Delete old home-manager generations (older than 30 days)
home-manager expire-generations "-30 days"

# 2. Collect garbage to actually free the space
nix-collect-garbage -d
```
3\. The "It worked yesterday" Fix (Rollbacks)

The Symptom: You ran hm-switch, and now your shell is broken or a tool stopped working.

The Fix: Nix keeps a history of your environments.
```bash 
# List your previous versions
home-manager generations

# Roll back to a specific working version (e.g., generation 42)
~/.local/state/nix/profiles/home-manager-42-link/activate
```

Finally, if you are sick of nix, you can uninstall it with this command:
```
/nix/nix-installer uninstall
```
"Wait, why I should be sick of nix?"
It is not all sunshine and rainbows. Here are some things you have to learn.
## Caveats and Gotchas
Before you start using nix as your package manager, I want to give some caveats and "gotchas" regarding Nix:

1.  **Nix (the language) and Nix (the package manager)** are not the same as NixOS. You do not need to download NixOS to use Nix.
    
2.  **System Constraints:** Because of the above, things like Docker, the Kernel, Drivers, and Networking (anything requiring sudo) cannot be handled by Nix on a foreign OS. NixOS was specifically designed to solve this at the OS level.
    
3.  **Impure Binaries Problem:** If you download a pre-compiled library, it may try to bind to a library in a standard location (e.g., /usr/lib/ld-linux.so). This may crash a perfectly fine program. To solve this, you can use a tool called patchelf.
    
4.  **Disk Space Bloat:** You will likely end up with duplicate packages for the same software. Although Nix provides a smart garbage collector, you must run nix-collect-garbage -d from time to time.
    
5.  **Read-Only Philosophy:** Nix is great at "faking" stuff to make things work. Your system may have a .bashrc that looks normal, but you cannot edit it if it is managed by Nix. It is likely a symlink to an object in the immutable /nix/store. While you can force an edit as a superuser, you risk breaking the environment's integrity.
    
6.  **Path Variable Shadowing:** If you have git installed via apt and git installed via Nix, which git will point to the Nix version. This can cause confusion if the versions differ significantly or if the Nix version lacks a specific system-level plugin.
