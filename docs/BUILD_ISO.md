# FusionOS - Guia de Compilação da Imagem ISO

Este guia detalha como compilar a imagem `.iso` oficial do **FusionOS** pronta para gravação em pendrive USB ou teste em Máquinas Virtuais (VirtualBox, VMware, QEMU).

---

## Métodos de Compilação

Para compilar uma ISO baseada em Fedora, o processo exige um ambiente Linux com privilégios de `root` (pois é necessário criar sistemas de arquivos e realizar `chroot`).

Você pode compilar utilizando:
1. **Uma Máquina Virtual com Fedora 40/41** (Método mais simples e recomendado).
2. **WSL2 no Windows** (com suporte a loop devices).
3. **Um computador físico com Fedora instalado**.

---

## Passo a Passo (Em Máquina Virtual Fedora ou Linux Nativo)

### 1. Clonar ou copiar a pasta do projeto `HEAK`
Transfira os arquivos deste repositório para o ambiente de compilação:
```bash
git clone <seu-repositorio> FusionOS
# ou copie a pasta HEAK para a máquina
cd HEAK
```

### 2. Tornar os scripts executáveis
```bash
chmod +x scripts/*.sh configs/wine/*.sh
```

### 3. Instalar as ferramentas de criação de ISO
```bash
sudo dnf install -y lorax pykickstart
```

### 4. Validar o arquivo Kickstart
Antes de iniciar a compilação, confirme se a receita de pacotes é válida:
```bash
ksvalidator kickstart/fusionos-fedora.ks
```
*(Se o comando retornar sem erros, a receita está 100% pronta).*

### 5. Iniciar a compilação da ISO
Execute o script automatizado:
```bash
sudo ./scripts/build-iso.sh
```

O script realizará:
* Download dos pacotes RPM oficiais e codecs.
* Criação do ambiente live com o KDE Plasma 6 customizado.
* Injeção dos scripts do FusionOS, Wine Handler e Chameleon Engine.
* Geração do arquivo final: `output/FusionOS-Live-x86_64.iso`.

---

## Como Gravar no Pendrive USB

Após a geração da ISO, utilize um dos programas recomendados:
* **BalenaEtcher** (Windows/Mac/Linux): Basta selecionar o arquivo `.iso`, selecionar o pendrive e clicar em "Flash!".
* **Ventoy**: Copie o arquivo `.iso` diretamente para um pendrive configurado com Ventoy.
* **Rufus** (Windows): Selecione a ISO e grave no modo "DD" ou "ISO".

---

## Como Testar no VirtualBox / VMware

1. Crie uma nova máquina virtual:
   * **Tipo:** Linux
   * **Versão:** Fedora (64-bit)
   * **Memória RAM:** Mínimo de 4 GB (recomendado 8 GB).
   * **Processadores:** 2 a 4 vCPUs.
   * **Gráficos:** Habilite "Aceleração 3D" e defina a memória de vídeo em 128 MB.
2. Aponte o drive de CD/DVD virtual para a ISO gerada.
3. Inicie a máquina. O sistema entrará direto no **FusionOS Live**, já com a interface padrão macOS, Spotlight no `Alt+Espaço` e alternador de layout funcional.

