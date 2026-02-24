start_word = "KEDI"
target_word = "YEDI"
frontier = [start_word]
explored = set()
print(f"başlangıç: {start_word}  -> hedef: {target_word}")

while len(frontier) > 0:
    current = frontier.pop(0)
    if current == target_word:
        print("hedefe ulaşıldı")
        break

    explored.add(current)
    print(f"şuan ki  kelime: {current}")