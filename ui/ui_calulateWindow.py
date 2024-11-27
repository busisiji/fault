from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QScrollArea, QGroupBox, QHBoxLayout, \
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QMessageBox, QTextEdit, QInputDialog, \
    QApplication
from PyQt5.QtCore import Qt

from ui.others.ui_fun import BaseWindow
from ui.qss import btn_css

products_types = ['I型', 'II型']
material_types = ['A', 'B', 'C']
material_nums = [[3, 5, 2]]
# 产品原材料配方 {产品型号:{物料类型:数量}}
product_recipe = {
    'I型': {'A': 3, 'B': 5, 'C': 2},
    'II型': {'A': 2, 'B': 4, 'C': 1}
}

class OrderInventoryApp(BaseWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("订单物料统计系统")

        # 布局管理
        layout = QVBoxLayout()

        # 产品配方输入
        recipe_group_box = QGroupBox("产品配方配置")
        recipe_layout = QVBoxLayout()

        # 创建表格
        self.recipe_table = QTableWidget()
        self.recipe_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.recipe_table.setFixedHeight(300)
        self.recipe_table.setColumnCount(len(material_types))
        self.recipe_table.setHorizontalHeaderLabels(material_types)
        self.recipe_table.setRowCount(len(products_types))
        self.recipe_table.setVerticalHeaderLabels(products_types)
        self.recipe_table.setStyleSheet(self.table_style)

        # 初始化表格数据
        for i, product in enumerate(products_types):
            for j, part in enumerate(material_types):
                quantity = product_recipe.get(product, {}).get(part, 0)
                item = QTableWidgetItem(str(quantity))
                self.recipe_table.setItem(i, j, item)


        # 调整列宽和行高
        header = self.recipe_table.horizontalHeader()
        for i in range(len(material_types)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        # 添加水平和垂直滚动条
        self.recipe_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.recipe_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        recipe_layout.addWidget(self.recipe_table)

        # 添加和删除产品型号和物料类型的按钮
        button_layout = QHBoxLayout()

        self.add_product_button = QPushButton("添加产品型号")
        btn_css(self.add_product_button)
        self.add_product_button.clicked.connect(self.add_product)
        button_layout.addWidget(self.add_product_button)

        self.delete_product_button = QPushButton("删除产品型号")
        btn_css(self.delete_product_button)
        self.delete_product_button.clicked.connect(self.delete_product)
        button_layout.addWidget(self.delete_product_button)

        self.add_material_button = QPushButton("添加物料类型")
        btn_css(self.add_material_button)
        self.add_material_button.clicked.connect(self.add_material)
        button_layout.addWidget(self.add_material_button)

        self.delete_material_button = QPushButton("删除物料类型")
        btn_css(self.delete_material_button)
        self.delete_material_button.clicked.connect(self.delete_material)
        button_layout.addWidget(self.delete_material_button)

        recipe_layout.addLayout(button_layout)

        # 更新配方按钮
        self.update_recipe_button = QPushButton("更新配方")
        btn_css(self.update_recipe_button)
        self.update_recipe_button.clicked.connect(self.update_recipe)
        recipe_layout.addWidget(self.update_recipe_button)

        recipe_group_box.setLayout(recipe_layout)
        layout.addWidget(recipe_group_box)

        # 订单信息输入
        order_group_box = QGroupBox("订单信息输入")
        order_layout = QVBoxLayout()

        # 创建滚动区域
        order_scroll_area = QScrollArea()
        order_scroll_area.setWidgetResizable(True)
        order_scroll_widget = QWidget()
        order_scroll_area.setWidget(order_scroll_widget)

        self.order_form = QFormLayout()
        order_scroll_widget.setLayout(self.order_form)

        self.order_entries = {}
        for product in product_recipe.keys():
            label = QLabel(f"{product} 数量:")
            entry = QLineEdit()
            self.order_form.addRow(label, entry)
            self.order_entries[product] = entry

        order_layout.addWidget(order_scroll_area)
        order_group_box.setLayout(order_layout)
        layout.addWidget(order_group_box)

        # 库存信息输入
        inventory_group_box = QGroupBox("库存信息输入")
        inventory_layout = QVBoxLayout()

        # 创建滚动区域
        inventory_scroll_area = QScrollArea()
        inventory_scroll_area.setWidgetResizable(True)
        inventory_scroll_widget = QWidget()
        inventory_scroll_area.setWidget(inventory_scroll_widget)

        self.inventory_form = QFormLayout()
        inventory_scroll_widget.setLayout(self.inventory_form)

        self.inventory_entries = {}
        for part in material_types:
            label = QLabel(f"{part} 零件库存:")
            entry = QLineEdit()
            self.inventory_form.addRow(label, entry)
            self.inventory_entries[part] = entry

        inventory_layout.addWidget(inventory_scroll_area)
        inventory_group_box.setLayout(inventory_layout)
        layout.addWidget(inventory_group_box)

        # 计算按钮
        self.calculate_button = QPushButton("计算")
        btn_css(self.calculate_button)
        self.calculate_button.clicked.connect(self.calculate_requirements)
        layout.addWidget(self.calculate_button)

        # 结果显示
        result_layout = QVBoxLayout()

        self.required_parts_label = QLabel("所需零件数量:")
        result_layout.addWidget(self.required_parts_label)

        self.required_parts_text = QTextEdit()
        result_layout.addWidget(self.required_parts_text)

        self.remaining_inventory_label = QLabel("剩余库存:")
        result_layout.addWidget(self.remaining_inventory_label)

        self.remaining_inventory_text = QTextEdit()
        result_layout.addWidget(self.remaining_inventory_text)

        self.additional_parts_needed_label = QLabel("需补充的零件数量:")
        result_layout.addWidget(self.additional_parts_needed_label)

        self.additional_parts_needed_text = QTextEdit()
        result_layout.addWidget(self.additional_parts_needed_text)

        layout.addLayout(result_layout)

        self.setLayout(layout)

    def add_product(self):
        text, ok = QInputDialog.getText(self, '添加产品型号', '请输入新的产品型号:')
        if ok and text:
            if text not in products_types:
                products_types.append(text)
                product_recipe[text] = {part: 0 for part in material_types}
                self.update_table()
                self.update_order_form()
                self.update_inventory_form()

    def delete_product(self):
        items, ok = QInputDialog.getItem(self, '删除产品型号', '请选择要删除的产品型号:', products_types, 0, False)
        if ok and items:
            products_types.remove(items)
            del product_recipe[items]
            self.update_table()
            self.update_order_form()

    def add_material(self):
        text, ok = QInputDialog.getText(self, '添加物料类型', '请输入新的物料类型:')
        if ok and text:
            if text not in material_types:
                material_types.append(text)
                for product in products_types:
                    product_recipe[product][text] = 0
                self.update_table()
                self.update_inventory_form()

    def delete_material(self):
        items, ok = QInputDialog.getItem(self, '删除物料类型', '请选择要删除的物料类型:', material_types, 0, False)
        if ok and items:
            material_types.remove(items)
            for product in products_types:
                del product_recipe[product][items]
            self.update_table()
            self.update_inventory_form()

    def update_table(self):
        self.recipe_table.setColumnCount(len(material_types))
        self.recipe_table.setHorizontalHeaderLabels(material_types)
        self.recipe_table.setRowCount(len(products_types))
        self.recipe_table.setVerticalHeaderLabels(products_types)

        for i, product in enumerate(products_types):
            for j, part in enumerate(material_types):
                quantity = product_recipe.get(product, {}).get(part, 0)
                item = QTableWidgetItem(str(quantity))
                self.recipe_table.setItem(i, j, item)

    def update_order_form(self):
        # 清除旧的订单信息输入
        while self.order_form.count():
            item = self.order_form.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 重新创建订单信息输入
        self.order_entries = {}
        for product in product_recipe.keys():
            label = QLabel(f"{product} 数量:")
            entry = QLineEdit()
            self.order_form.addRow(label, entry)
            self.order_entries[product] = entry

    def update_inventory_form(self):
        # 清除旧的库存信息输入
        while self.inventory_form.count():
            item = self.inventory_form.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 重新创建库存信息输入
        self.inventory_entries = {}
        for part in material_types:
            label = QLabel(f"{part} 零件库存:")
            entry = QLineEdit()
            self.inventory_form.addRow(label, entry)
            self.inventory_entries[part] = entry

    def update_recipe(self):
        # 获取用户输入的配方信息
        updated_recipe = {}
        for i in range(self.recipe_table.rowCount()):
            product = self.recipe_table.verticalHeaderItem(i).text()
            updated_recipe[product] = {}
            for j in range(self.recipe_table.columnCount()):
                part = self.recipe_table.horizontalHeaderItem(j).text()
                try:
                    quantity = int(self.recipe_table.item(i, j).text().strip())
                    updated_recipe[product][part] = quantity
                except ValueError:
                    QMessageBox.critical(self, "输入错误", f"请输入有效的数字: {product} - {part} 数量")
                    return

        # 更新全局变量 product_recipe
        global product_recipe
        product_recipe = updated_recipe

        # 更新订单信息输入和库存信息输入
        self.update_order_form()
        self.update_inventory_form()

        # 提示用户更新成功
        QMessageBox.information(self, "更新成功", "产品配方已成功更新！")

    def calculate_requirements(self):
        # 获取订单信息
        order = {}
        for product, entry in self.order_entries.items():
            try:
                quantity = int(entry.text().strip())
                if quantity < 0:
                    raise ValueError("数量不能为负数")
                order[product] = quantity
            except ValueError as e:
                QMessageBox.critical(self, "输入错误", f"请输入有效的数字: {product} 数量 - {str(e)}")
                return

        # 获取库存信息
        inventory = {}
        for part, entry in self.inventory_entries.items():
            try:
                quantity = int(entry.text().strip())
                if quantity < 0:
                    raise ValueError("库存数量不能为负数")
                inventory[part] = quantity
            except ValueError as e:
                QMessageBox.critical(self, "输入错误", f"请输入有效的数字: {part} 零件库存 - {str(e)}")
                return

        # 计算所需零件数量、剩余库存及需补充的零件数量
        required_parts, remaining_inventory, additional_parts_needed = self.compute_requirements(order, inventory, product_recipe)

        # 显示结果
        self.required_parts_text.clear()
        self.required_parts_text.append("\n".join([f"{part}: {quantity}" for part, quantity in required_parts.items()]))

        self.remaining_inventory_text.clear()
        self.remaining_inventory_text.append("\n".join([f"{part}: {quantity}" for part, quantity in remaining_inventory.items()]))

        self.additional_parts_needed_text.clear()
        self.additional_parts_needed_text.append("\n".join([f"{part}: {quantity}" for part, quantity in additional_parts_needed.items() if quantity > 0]))

    def compute_requirements(self, order, inventory, recipe):
        required_parts = {part: 0 for part in material_types}
        for product, quantity in order.items():
            for part, count in recipe.get(product, {}).items():
                required_parts[part] += count * quantity

        remaining_inventory = inventory.copy()
        additional_parts_needed = {part: 0 for part in required_parts}

        for part, required in required_parts.items():
            if required <= inventory.get(part, 0):
                remaining_inventory[part] -= required
            else:
                additional_parts_needed[part] = required - inventory.get(part, 0)
                remaining_inventory[part] = 0

        return required_parts, remaining_inventory, additional_parts_needed

def main():
    app = QApplication([])
    ex = OrderInventoryApp()
    ex.show()
    app.exec_()

if __name__ == "__main__":
    main()
