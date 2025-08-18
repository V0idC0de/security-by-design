# GitHub Workflows Demo

Diese Demo zeigt die Verwendung von GitHub Workflows in einem Demo-Repository, das mit Terraform erstellt wurde.

## Voraussetzungen

- [GitHub CLI](https://cli.github.com/) installiert und authentifiziert (`gh auth login`)
- [Terraform](https://www.terraform.io/) installiert

## Aufbau des Demo-Repositories

1. Mit GitHub CLI authentifizieren:

    ```sh
    gh auth login
    ```

2. Terraform initialisieren:

    ```sh
    terraform init
    ```

3. Konfiguration anwenden:

    ```sh
    terraform apply
    ```

Das Repository wird im authentifizierten GitHub-Account erstellt.

## Abbau des Demo-Repositories

Um alle durch diese Demo erstellten Ressourcen zu entfernen:

```sh
terraform destroy
```
