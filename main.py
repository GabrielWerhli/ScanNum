from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QLabel, QFileDialog, QHBoxLayout, QMessageBox
)
from PIL import Image
import pytesseract
import re
import sys
import os

class WhatsAppNumberExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extractor de Números WhatsApp")
        self.resize(700, 500)

        # 1) Aponte diretamente para o executável do Tesseract:
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
        # (Altere este caminho se você instalou em outra pasta.)

        layout = QVBoxLayout(self)

        # preview / instruções
        self.img_label = QLabel("Selecione uma imagem ou várias imagens")
        self.img_label.setFixedHeight(250)
        self.img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.img_label)

        # botões
        h = QHBoxLayout()
        btn_load = QPushButton("Selecionar Imagens")
        btn_load.clicked.connect(self.load_images)
        h.addWidget(btn_load)
        btn_ocr = QPushButton("Processar OCR")
        btn_ocr.clicked.connect(self.process_ocr)
        h.addWidget(btn_ocr)
        layout.addLayout(h)

        # resultado
        self.list_numbers = QListWidget()
        layout.addWidget(self.list_numbers)

        btn_copy = QPushButton("Copiar Tudo")
        btn_copy.clicked.connect(self.copy_numbers)
        layout.addWidget(btn_copy)

        self.image_paths = []

    def load_images(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Abrir Imagens", "", "Imagens (*.png *.jpg *.jpeg *.bmp)"
        )
        if not paths:
            return
        self.image_paths = paths
        pix = QPixmap(paths[0]).scaled(
            self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.img_label.setPixmap(pix)

    def preprocess(self, path):
        img = Image.open(path).convert("L")
        return img.point(lambda x: 0 if x < 128 else 255, mode="1")

    def extract_numbers(self, text):
        # captura trechos com +, dígitos, espaços e hífens
        cand = re.findall(r"[\+\d][\d\-\s]{7,20}", text)
        nums = set()
        for c in cand:
            n = re.sub(r"[^\d\+]", "", c)
            if re.fullmatch(r"\+?[1-9]\d{7,14}", n):
                nums.add(n)
        return nums

    def process_ocr(self):
        if not self.image_paths:
            QMessageBox.warning(self, "Atenção", "Nenhuma imagem selecionada.")
            return

        all_nums = set()
        QMessageBox.information(
            self, "Processando",
            f"Extraindo números de {len(self.image_paths)} imagem(ns)…"
        )

        for p in self.image_paths:
            img = self.preprocess(p)
            # não especificamos lang: usa o padrão (inglês), que já lê dígitos
            text = pytesseract.image_to_string(img)
            all_nums |= self.extract_numbers(text)

        self.list_numbers.clear()
        for n in sorted(all_nums):
            self.list_numbers.addItem(n)

        QMessageBox.information(
            self, "Concluído",
            f"Foram encontrados {len(all_nums)} números únicos."
        )

    def copy_numbers(self):
        cnt = self.list_numbers.count()
        if cnt == 0:
            QMessageBox.information(self, "Info", "Nenhum número para copiar.")
            return
        items = [self.list_numbers.item(i).text() for i in range(cnt)]
        QApplication.clipboard().setText("\n".join(items))
        QMessageBox.information(self, "Copiado", f"{cnt} número(s) copiado(s).")

if __name__ == "__main__":
    # checa dependências
    try:
        import PySide6, pytesseract
        from PIL import Image
    except ImportError as e:
        print("Instale:", e.name, "→ pip install PySide6 pytesseract pillow")
        sys.exit(1)

    app = QApplication(sys.argv)
    w = WhatsAppNumberExtractor()
    w.show()
    sys.exit(app.exec())
