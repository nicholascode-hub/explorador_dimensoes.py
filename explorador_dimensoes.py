import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import io
import threading

# ====== API DO RICK AND MORTY ======
BASE_URL = "https://rickandmortyapi.com/api"

def buscar_localizacoes(pagina=1):
    """Busca localizações da API"""
    try:
        response = requests.get(f"{BASE_URL}/location?page={pagina}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Erro ao buscar localizações: {e}")
        return None

def buscar_todas_localizacoes():
    """Busca todas as localizações (todas as páginas)"""
    localizacoes = []
    pagina = 1
    
    while True:
        dados = buscar_localizacoes(pagina)
        if not dados or 'results' not in dados:
            break
        
        localizacoes.extend(dados['results'])
        
        # Verifica se há próxima página
        if not dados['info'].get('next'):
            break
        
        pagina += 1
    
    return localizacoes

def buscar_personagem(url):
    """Busca informações de um personagem específico"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def buscar_imagem_personagem(url):
    """Baixa imagem de um personagem"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        return None
    except:
        return None

# ====== INTERFACE GRÁFICA ======
class ExploradorDimensoes:
    def __init__(self, root):
        self.root = root
        self.root.title("🌌 Explorador de Dimensões - Rick and Morty")
        self.root.geometry("1200x800")
        
        self.localizacoes = []
        self.localizacao_selecionada = None
        self.imagens_cache = {}
        
        self.criar_interface()
        self.carregar_localizacoes_thread()
    
    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Título
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 10))
        
        titulo = ttk.Label(
            header_frame,
            text="🌌 Explorador de Dimensões",
            font=("Arial", 28, "bold"),
            bootstyle="success"
        )
        titulo.pack(side=LEFT)
        
        # Status/Loading
        self.lbl_status = ttk.Label(
            header_frame,
            text="Carregando dimensões...",
            font=("Arial", 11),
            bootstyle="info"
        )
        self.lbl_status.pack(side=RIGHT, padx=10)
        
        # Frame de busca
        search_frame = ttk.LabelFrame(main_frame, text="🔍 Buscar Localização", padding=10)
        search_frame.pack(fill=X, pady=10)
        
        ttk.Label(search_frame, text="Nome:", font=("Arial", 10)).pack(side=LEFT, padx=5)
        
        self.entry_busca = ttk.Entry(search_frame, width=40)
        self.entry_busca.pack(side=LEFT, padx=5)
        self.entry_busca.bind('<KeyRelease>', lambda e: self.filtrar_localizacoes())
        
        btn_limpar = ttk.Button(
            search_frame,
            text="🔄 Limpar",
            command=self.limpar_busca,
            bootstyle="secondary-outline",
            width=12
        )
        btn_limpar.pack(side=LEFT, padx=5)
        
        self.lbl_total = ttk.Label(
            search_frame,
            text="Total: 0 localizações",
            font=("Arial", 10, "bold")
        )
        self.lbl_total.pack(side=RIGHT, padx=10)
        
        # Painel dividido
        paned = ttk.PanedWindow(main_frame, orient=HORIZONTAL)
        paned.pack(fill=BOTH, expand=YES, pady=10)
        
        # ==== LADO ESQUERDO: Lista de Localizações ====
        left_frame = ttk.LabelFrame(paned, text="📍 Localizações & Dimensões", padding=10)
        paned.add(left_frame, weight=1)
        
        # Treeview para lista
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=BOTH, expand=YES)
        
        scrollbar_tree = ttk.Scrollbar(tree_frame)
        scrollbar_tree.pack(side=RIGHT, fill=Y)
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("nome", "tipo", "dimensao", "residentes"),
            show="headings",
            yscrollcommand=scrollbar_tree.set,
            selectmode="browse"
        )
        
        self.tree.heading("nome", text="Nome da Localização")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("dimensao", text="Dimensão")
        self.tree.heading("residentes", text="Residentes")
        
        self.tree.column("nome", width=250)
        self.tree.column("tipo", width=120)
        self.tree.column("dimensao", width=150)
        self.tree.column("residentes", width=80, anchor=CENTER)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar_tree.config(command=self.tree.yview)
        
        self.tree.bind('<<TreeviewSelect>>', self.ao_selecionar_localizacao)
        
        # ==== LADO DIREITO: Detalhes ====
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # Informações da localização
        info_frame = ttk.LabelFrame(right_frame, text="📋 Informações Detalhadas", padding=15)
        info_frame.pack(fill=X, pady=(0, 10))
        
        self.text_info = scrolledtext.ScrolledText(
            info_frame,
            height=8,
            font=("Courier New", 10),
            wrap=tk.WORD,
            state='disabled'
        )
        self.text_info.pack(fill=BOTH, expand=YES)
        
        # Lista de residentes
        residentes_frame = ttk.LabelFrame(right_frame, text="👥 Residentes Conhecidos", padding=10)
        residentes_frame.pack(fill=BOTH, expand=YES)
        
        # Canvas com scroll para residentes
        canvas_frame = ttk.Frame(residentes_frame)
        canvas_frame.pack(fill=BOTH, expand=YES)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#2b3e50", highlightthickness=0)
        scrollbar_residentes = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        
        self.frame_residentes = ttk.Frame(self.canvas)
        self.frame_residentes.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.frame_residentes, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_residentes.set)
        
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar_residentes.pack(side=RIGHT, fill=Y)
        
        # Bind scroll do mouse
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Botões de ação
        btn_frame = ttk.Frame(residentes_frame)
        btn_frame.pack(fill=X, pady=(10, 0))
        
        btn_aleatorio = ttk.Button(
            btn_frame,
            text="🎲 Dimensão Aleatória",
            command=self.selecionar_aleatorio,
            bootstyle="warning",
            width=25
        )
        btn_aleatorio.pack(side=LEFT, padx=5)
        
        btn_estatisticas = ttk.Button(
            btn_frame,
            text="📊 Estatísticas Gerais",
            command=self.mostrar_estatisticas,
            bootstyle="info-outline",
            width=25
        )
        btn_estatisticas.pack(side=LEFT, padx=5)
    
    def _on_mousewheel(self, event):
        """Scroll com mouse wheel"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def carregar_localizacoes_thread(self):
        """Carrega localizações em thread separada"""
        def carregar():
            self.lbl_status.config(text="⏳ Carregando dimensões da API...")
            self.localizacoes = buscar_todas_localizacoes()
            
            self.root.after(0, self.atualizar_lista)
            self.root.after(0, lambda: self.lbl_status.config(
                text=f"✅ {len(self.localizacoes)} localizações carregadas!"
            ))
        
        thread = threading.Thread(target=carregar, daemon=True)
        thread.start()
    
    def atualizar_lista(self, localizacoes=None):
        """Atualiza a lista de localizações na treeview"""
        if localizacoes is None:
            localizacoes = self.localizacoes
        
        # Limpa treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adiciona localizações
        for loc in localizacoes:
            self.tree.insert(
                "",
                "end",
                values=(
                    loc['name'],
                    loc['type'],
                    loc['dimension'],
                    len(loc['residents'])
                ),
                tags=(loc['id'],)
            )
        
        self.lbl_total.config(text=f"Total: {len(localizacoes)} localizações")
    
    def filtrar_localizacoes(self):
        """Filtra localizações por nome"""
        termo = self.entry_busca.get().lower()
        
        if not termo:
            self.atualizar_lista()
            return
        
        filtradas = [
            loc for loc in self.localizacoes
            if termo in loc['name'].lower() or 
               termo in loc['type'].lower() or
               termo in loc['dimension'].lower()
        ]
        
        self.atualizar_lista(filtradas)
    
    def limpar_busca(self):
        """Limpa campo de busca"""
        self.entry_busca.delete(0, tk.END)
        self.atualizar_lista()
    
    def ao_selecionar_localizacao(self, event):
        """Evento ao selecionar uma localização"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        loc_id = int(item['tags'][0])
        
        # Encontra localização
        self.localizacao_selecionada = next(
            (loc for loc in self.localizacoes if loc['id'] == loc_id),
            None
        )
        
        if self.localizacao_selecionada:
            self.mostrar_detalhes()
    
    def mostrar_detalhes(self):
        """Mostra detalhes da localização selecionada"""
        loc = self.localizacao_selecionada
        
        # Atualiza texto de informações
        self.text_info.config(state='normal')
        self.text_info.delete(1.0, tk.END)
        
        info = f"""
╔══════════════════════════════════════════════════════╗
  📍 {loc['name']}
╚══════════════════════════════════════════════════════╝

🏷️  Tipo: {loc['type']}
🌍 Dimensão: {loc['dimension']}
👥 Residentes Conhecidos: {len(loc['residents'])}
🆔 ID: {loc['id']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        self.text_info.insert(1.0, info)
        self.text_info.config(state='disabled')
        
        # Carrega residentes
        self.carregar_residentes()
    
    def carregar_residentes(self):
        """Carrega e exibe residentes da localização"""
        # Limpa frame de residentes
        for widget in self.frame_residentes.winfo_children():
            widget.destroy()
        
        loc = self.localizacao_selecionada
        
        if not loc['residents']:
            ttk.Label(
                self.frame_residentes,
                text="Nenhum residente conhecido nesta localização 🤷‍♂️",
                font=("Arial", 12),
                bootstyle="warning"
            ).pack(pady=50)
            return
        
        # Label de carregamento
        lbl_loading = ttk.Label(
            self.frame_residentes,
            text="⏳ Carregando residentes...",
            font=("Arial", 12)
        )
        lbl_loading.pack(pady=20)
        
        # Carrega em thread
        def carregar():
            residentes_info = []
            for url in loc['residents'][:20]:  # Limita a 20 para não sobrecarregar
                personagem = buscar_personagem(url)
                if personagem:
                    residentes_info.append(personagem)
            
            self.root.after(0, lambda: self.exibir_residentes(residentes_info))
        
        threading.Thread(target=carregar, daemon=True).start()
    
    def exibir_residentes(self, residentes):
        """Exibe cards dos residentes"""
        # Limpa frame
        for widget in self.frame_residentes.winfo_children():
            widget.destroy()
        
        if not residentes:
            ttk.Label(
                self.frame_residentes,
                text="Erro ao carregar residentes 😕",
                font=("Arial", 12)
            ).pack(pady=50)
            return
        
        # Cria cards
        for i, personagem in enumerate(residentes):
            self.criar_card_personagem(personagem, i)
    
    def criar_card_personagem(self, personagem, index):
        """Cria um card visual para o personagem"""
        # Frame do card
        card = ttk.Frame(self.frame_residentes, bootstyle="dark")
        card.pack(fill=X, padx=10, pady=5)
        
        # Frame interno
        inner = ttk.Frame(card, padding=10)
        inner.pack(fill=X)
        
        # Imagem (carrega em thread)
        img_label = ttk.Label(inner, text="📷")
        img_label.pack(side=LEFT, padx=10)
        
        def carregar_img():
            if personagem['id'] not in self.imagens_cache:
                img = buscar_imagem_personagem(personagem['image'])
                if img:
                    # Compatibilidade com diferentes versões do Pillow
                    try:
                        resample = Image.Resampling.LANCZOS
                    except AttributeError:
                        resample = Image.LANCZOS
                    img = img.resize((80, 80), resample)
                    self.imagens_cache[personagem['id']] = ImageTk.PhotoImage(img)
            
            if personagem['id'] in self.imagens_cache:
                # Atualiza imagem protegendo contra widget destruído
                def atualizar_label():
                    try:
                        img_label.config(
                            image=self.imagens_cache[personagem['id']],
                            text=""
                        )
                    except tk.TclError:
                        # Widget destruído; ignora atualização
                        pass
                self.root.after(0, atualizar_label)
        
        threading.Thread(target=carregar_img, daemon=True).start()
        
        # Informações
        info_frame = ttk.Frame(inner)
        info_frame.pack(side=LEFT, fill=X, expand=YES, padx=10)
        
        # Nome
        ttk.Label(
            info_frame,
            text=personagem.get('name', 'Desconhecido'),
            font=("Arial", 13, "bold"),
            bootstyle="success"
        ).pack(anchor=tk.W)
        
        # Status
        status_color = {
            'Alive': 'success',
            'Dead': 'danger',
            'unknown': 'warning'
        }.get(personagem.get('status'), 'secondary')
        
        ttk.Label(
            info_frame,
            text=f"Status: {personagem.get('status', 'unknown')} • {personagem.get('species', '')}",
            font=("Arial", 10),
            bootstyle=status_color
        ).pack(anchor=tk.W)
        
        # Gênero / Origem
        origem = personagem.get('origin', {}).get('name', 'Desconhecido')
        ttk.Label(
            info_frame,
            text=f"Gênero: {personagem.get('gender', 'Desconhecido')} • Origem: {origem}",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(anchor=tk.W)
    
    def selecionar_aleatorio(self):
        """Seleciona uma localização aleatória"""
        import random
        
        if not self.localizacoes:
            messagebox.showwarning("Aviso", "Carregue as localizações primeiro!")
            return
        
        loc_aleatoria = random.choice(self.localizacoes)
        
        # Seleciona na treeview
        for item in self.tree.get_children():
            if int(self.tree.item(item)['tags'][0]) == loc_aleatoria['id']:
                self.tree.selection_set(item)
                self.tree.see(item)
                self.ao_selecionar_localizacao(None)
                break
    
    def mostrar_estatisticas(self):
        """Mostra estatísticas gerais"""
        if not self.localizacoes:
            messagebox.showinfo("Info", "Carregue as localizações primeiro!")
            return
        
        # Calcula estatísticas
        total_residentes = sum(len(loc['residents']) for loc in self.localizacoes)
        tipos = {}
        dimensoes = {}
        
        for loc in self.localizacoes:
            tipos[loc['type']] = tipos.get(loc['type'], 0) + 1
            dimensoes[loc['dimension']] = dimensoes.get(loc['dimension'], 0) + 1
        
        tipo_mais_comum = max(tipos, key=tipos.get)
        dimensao_mais_comum = max(dimensoes, key=dimensoes.get)
        
        # Localização com mais residentes
        loc_mais_populosa = max(self.localizacoes, key=lambda x: len(x['residents']))
        
        msg = f"""
📊 ESTATÍSTICAS GERAIS DO MULTIVERSO

🌍 Total de Localizações: {len(self.localizacoes)}
👥 Total de Residentes Conhecidos: {total_residentes}

📍 Tipo Mais Comum: {tipo_mais_comum} ({tipos[tipo_mais_comum]} locais)
🌌 Dimensão Mais Comum: {dimensao_mais_comum} ({dimensoes[dimensao_mais_comum]} locais)

🏆 Localização Mais Populosa:
   {loc_mais_populosa['name']} 
   ({len(loc_mais_populosa['residents'])} residentes)

📈 Tipos Únicos: {len(tipos)}
🔀 Dimensões Únicas: {len(dimensoes)}
        """
        
        messagebox.showinfo("📊 Estatísticas do Multiverso", msg)

# ====== EXECUTAR APLICAÇÃO ======
if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = ExploradorDimensoes(root)
    root.mainloop()