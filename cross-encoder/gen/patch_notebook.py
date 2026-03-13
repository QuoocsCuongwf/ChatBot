import json

NB_PATH = r"d:\SGU\CNTT\NCKH2025_2026\ChatBot\cross-encoder\gen\Untitled10 (3).ipynb"

with open(NB_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell["source"])

    # --- Patch 1: cell worker ---
    if "def worker(worker_id, batch_list):" in src and "global_chunk_counter % 5 == 0" in src:
        new_src = [
            "def worker(worker_id, batch_list):\n",
            "\n",
            "    global global_chunk_counter\n",
            "\n",
            "    output_file = os.path.join(OUTPUT_DIR, f\"worker_{worker_id}.jsonl\")\n",
            "    chunks_done_local = 0  # đếm số chunk worker này đã xử lý\n",
            "\n",
            "    with open(output_file, \"a\", encoding=\"utf-8\") as f:\n",
            "\n",
            "        for batch in tqdm(batch_list, desc=f\"Worker {worker_id}\"):\n",
            "\n",
            "            result = generate_batch(batch)\n",
            "\n",
            "            if result is None:\n",
            "                chunks_done_local += len(batch)\n",
            "                continue\n",
            "\n",
            "            for idx, queries in result.items():\n",
            "\n",
            "                idx = int(idx)\n",
            "\n",
            "                passage = batch[idx][\"text\"]\n",
            "\n",
            "                meta = batch[idx].get(\"metadata\", {})\n",
            "\n",
            "                for q in queries:\n",
            "\n",
            "                    record = {\n",
            "\n",
            "                        \"query\": q,\n",
            "                        \"passage\": passage,\n",
            "                        \"label\": 1,\n",
            "                        \"meta\": meta\n",
            "                    }\n",
            "\n",
            "                    f.write(json.dumps(record, ensure_ascii=False) + \"\\n\")\n",
            "\n",
            "            f.flush()\n",
            "\n",
            "            chunks_done_local += len(batch)\n",
            "\n",
            "            with checkpoint_lock:\n",
            "\n",
            "                global_chunk_counter += len(batch)\n",
            "\n",
            "                # Lưu checkpoint sau mỗi SAVE_EVERY chunks (theo Gen_data.ipynb)\n",
            "                if chunks_done_local % SAVE_EVERY == 0:\n",
            "\n",
            "                    save_checkpoint(global_chunk_counter)\n",
            "                    print(f\"  ↳ [Worker {worker_id}] Checkpoint {global_chunk_counter} chunks\")\n",
            "\n",
            "            time.sleep(1)",
        ]
        cell["source"] = new_src
        print("✅ Patched: worker() cell")

    # --- Patch 2: cell BATCH_SIZE / NUM_WORKERS — thêm SAVE_EVERY ---
    if "BATCH_SIZE = 5" in src and "NUM_WORKERS = 4" in src and "SAVE_EVERY" not in src:
        new_src = src.replace(
            "BATCH_SIZE = 5\n",
            "BATCH_SIZE = 5\n"
            "SAVE_EVERY = 5  # lưu checkpoint sau mỗi N chunks (theo Gen_data.ipynb)\n",
        )
        cell["source"] = list(new_src)  # store as list of chars? No — store as list of lines
        # Better: store as list of lines
        cell["source"] = [line + "\n" for line in new_src.splitlines()]
        # Fix last line (no trailing newline)
        if cell["source"]:
            cell["source"][-1] = cell["source"][-1].rstrip("\n")
        print("✅ Patched: BATCH_SIZE cell — added SAVE_EVERY")

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Done. Notebook saved.")
