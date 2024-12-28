import tkinter as tk
from tkinter import messagebox, simpledialog
from itertools import combinations_with_replacement

class PriceItem:
    def __init__(self, master, index, remove_callback):
        self.master = master
        self.index = index
        self.remove_callback = remove_callback
        self.min_count = 0
        self.active = True

        # 创建Frame来容纳每个价格项
        self.frame = tk.Frame(master)
        self.frame.pack(fill='x', pady=2)

        # 价格输入框
        self.price_var = tk.StringVar()
        self.entry_price = tk.Entry(self.frame, textvariable=self.price_var, width=10)
        self.entry_price.pack(side='left', padx=5)

        # 显示最小次数的标签
        self.label_min = tk.Label(self.frame, text="Min: 0")
        self.label_min.pack(side='left', padx=5)

        # 设置最小次数的按钮
        self.btn_set_min = tk.Button(self.frame, text="设置最小次数", command=self.set_min_count)
        self.btn_set_min.pack(side='left', padx=5)

        # 启用/禁用按钮
        self.btn_toggle = tk.Button(self.frame, text="禁用", command=self.toggle_active)
        self.btn_toggle.pack(side='left', padx=5)

        # 移除按钮
        self.btn_remove = tk.Button(self.frame, text="移除", command=self.remove)
        self.btn_remove.pack(side='left', padx=5)

    def set_min_count(self):
        try:
            count = simpledialog.askinteger("设置最小次数", "请输入最小出现次数（>=0）：", parent=self.master)
            if count is not None and count >= 0:
                self.min_count = count
                self.label_min.config(text=f"Min: {self.min_count}")
            else:
                messagebox.showerror("输入错误", "最小次数必须是非负整数。")
        except:
            messagebox.showerror("输入错误", "无效的输入。")

    def toggle_active(self):
        self.active = not self.active
        if self.active:
            self.btn_toggle.config(text="禁用")
            self.entry_price.config(state='normal')
            self.btn_set_min.config(state='normal')
        else:
            self.btn_toggle.config(text="启用")
            self.entry_price.config(state='disabled')
            self.btn_set_min.config(state='disabled')

    def remove(self):
        self.frame.destroy()
        self.remove_callback(self)

    def get_price(self):
        try:
            return float(self.price_var.get())
        except ValueError:
            raise ValueError(f"价格 '{self.price_var.get()}' 不是有效的数字。")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("满减优惠计算器")

        # 创建价格列表的Frame
        self.frame_prices = tk.Frame(root)
        self.frame_prices.pack(pady=10)

        # 添加价格项的按钮
        self.btn_add_price = tk.Button(root, text="添加商品价格", command=self.add_price_item)
        self.btn_add_price.pack(pady=5)

        # 初始化价格项列表
        self.price_items = []
        self.add_price_item()  # 默认添加一个价格项

        # 计算按钮
        self.btn_calculate = tk.Button(root, text="计算最佳组合", command=self.calculate)
        self.btn_calculate.pack(pady=10)

        # 结果显示框及其滚动条
        self.frame_result = tk.Frame(root)
        self.frame_result.pack()

        self.scrollbar = tk.Scrollbar(self.frame_result)
        self.scrollbar.pack(side='right', fill='y')

        self.text_result = tk.Text(self.frame_result, height=15, width=60, state='disabled', yscrollcommand=self.scrollbar.set)
        self.text_result.pack()

        self.scrollbar.config(command=self.text_result.yview)

    def add_price_item(self):
        if len(self.price_items) >= 20:
            messagebox.showwarning("限制", "最多只能添加20个商品价格。")
            return
        item = PriceItem(self.frame_prices, len(self.price_items)+1, self.remove_price_item)
        self.price_items.append(item)

    def remove_price_item(self, item):
        self.price_items.remove(item)

    def find_best_combinations(self, prices, counts):
        possible_combinations = []

        # 构建商品列表，考虑最小次数
        items = []
        for price, min_count in zip(prices, counts):
            items.extend([price] * min_count)

        # 剩余次数（假设每个商品最多可以选10次，可以根据需要调整）
        remaining_counts = [10 - count for count in counts]

        # 使用回溯法寻找组合
        def backtrack(start, current_sum, combination):
            if current_sum > 100:
                possible_combinations.append((current_sum, combination.copy()))
                return
            for i in range(start, len(prices)):
                if remaining_counts[i] > 0:
                    combination.append(prices[i])
                    remaining_counts[i] -= 1
                    backtrack(i, current_sum + prices[i], combination)
                    combination.pop()
                    remaining_counts[i] += 1

        backtrack(0, sum(items), items.copy())

        # 移除重复的组合
        unique_combinations = list({tuple(sorted(combo)): total for total, combo in possible_combinations}.items())
        unique_combinations = [(total, combo) for combo, total in unique_combinations]

        # 按照总和排序并返回前10个组合
        unique_combinations.sort(key=lambda x: x[0])
        return unique_combinations[:10]

    def calculate(self):
        try:
            active_prices = []
            min_counts = []
            for item in self.price_items:
                if item.active:
                    price = item.get_price()
                    active_prices.append(price)
                    min_counts.append(item.min_count)
            if not active_prices:
                raise ValueError("至少需要一个有效的商品价格。")

            # 计算最佳组合
            result = self.find_best_combinations(active_prices, min_counts)
            if not result:
                result_text = "没有找到符合条件的组合。"
            else:
                result_text = '\n'.join([f"总价: {total:.2f} 元, 组合: {combo}" for total, combo in result])

            # 显示结果
            self.text_result.config(state='normal')
            self.text_result.delete(1.0, tk.END)
            self.text_result.insert(tk.END, result_text)
            self.text_result.config(state='disabled')

        except ValueError as e:
            messagebox.showerror("输入错误", f"请检查输入格式: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
