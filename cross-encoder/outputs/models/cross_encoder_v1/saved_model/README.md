---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:13230
- loss:BinaryCrossEntropyLoss
base_model: cross-encoder/ms-marco-MiniLM-L6-v2
pipeline_tag: text-ranking
library_name: sentence-transformers
metrics:
- accuracy
- accuracy_threshold
- f1
- f1_threshold
- precision
- recall
- average_precision
model-index:
- name: CrossEncoder based on cross-encoder/ms-marco-MiniLM-L6-v2
  results:
  - task:
      type: cross-encoder-binary-classification
      name: Cross Encoder Binary Classification
    dataset:
      name: dev
      type: dev
    metrics:
    - type: accuracy
      value: 0.8915159944367177
      name: Accuracy
    - type: accuracy_threshold
      value: 1.584134817123413
      name: Accuracy Threshold
    - type: f1
      value: 0.8887451487710221
      name: F1
    - type: f1_threshold
      value: -0.18771395087242126
      name: F1 Threshold
    - type: precision
      value: 0.8307134220072552
      name: Precision
    - type: recall
      value: 0.9554937413073713
      name: Recall
    - type: average_precision
      value: 0.9522441932700629
      name: Average Precision
---

# CrossEncoder based on cross-encoder/ms-marco-MiniLM-L6-v2

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model finetuned from [cross-encoder/ms-marco-MiniLM-L6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
- **Base model:** [cross-encoder/ms-marco-MiniLM-L6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) <!-- at revision c5ee24cb16019beea0893ab7796b1df96625c6b8 -->
- **Maximum Sequence Length:** 256 tokens
- **Number of Output Labels:** 1 label
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Documentation:** [Cross Encoder Documentation](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Cross Encoders on Hugging Face](https://huggingface.co/models?library=sentence-transformers&other=cross-encoder)

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import CrossEncoder

# Download from the 🤗 Hub
model = CrossEncoder("cross_encoder_model_id")
# Get scores for pairs of texts
pairs = [
    ['Cơ quan nào có thẩm quyền ban hành văn bản, giấy tờ trong lĩnh vực văn hóa, thể thao và du lịch?', 'Khoản 1 Điều 24 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Giviones ĐẾN Ngày.13.76.12025 trong lĩnh vực văn hóa, thể thao và du lịch Văn bản, giấy tờ đã được cơ quan, người có thẩm quyền ban hành, cấp đang còn hiệu lực hoặc chưa hết thời hạn sử dụng trước khi Nghị định này có hiệu lực thì tiếp tục được sử dụng cho đến khi hết thời hạn ghi trong văn bản, giấy tờ đó.'],
    ['Điểm b Khoản 1 Điều 4 quy định về điều kiện gì?', 'Tại điểm b Khoản 1 Điều 4 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Người hy sinh thuộc cơ quan cấp xã và các trường hợp không thuộc quy định tại khoản 1, 2, 3,4 Điều 16 Nghị định số 131/2021/NĐ-CP và điểma'],
    ['Quỹ phòng, chống thiên tai được thành lập và quản lý như thế nào theo Nghị định này?', 'Khoản 1 Điều 6 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Tổ chức quản lý, phát triển chăn nuôi tại địa phương; thống kê, đánh tại điểm c khoản 2 Điều 80 Luật Chăn nuôi.'],
    ['Căn cứ vào văn bản nào để ban hành Nghị định này?', 'Khoản 3 Điều 16 NGHỊ ĐỊNH Ngày.13.1.6.2025 Quy định về phân quyền, phân cấp; phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực công tác dân tộc, tín ngưỡng, tôn giáo - Căn cứ Luật Tổ chức Chính phủ năm 2025; Trình tự, thủ tục tiếp nhận thông báo danh mục hoạt động tôn giáo quy định tại Mục XI Phụ lục I Nghị định này.'],
    ['Thẩm quyền phê duyệt nhiệm vụ quy hoạch của ai?', 'Khoản 3 Điều 11 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp, phân quyền, phân cấp trong lĩnh vực quy hoạch đô thị và nông thôn Gi ĐẾN Ngày. 13-16-12925 - Căn cứ Luật Tổ chức Chính phủ 2025; Không tổ chức lập, phê duyệt nhiệm vụ quy hoạch, quy hoạch đô thị và nông thôn đối với đô thị mới có phạm vi quy hoạch liên quan đến địa giới hành chính của từ 02 tỉnh trở lên theo quy định tại điểm a khoản 1 Điều 17 và điểm a khoản 1 điều 41.'],
]
scores = model.predict(pairs)
print(scores.shape)
# (5,)

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'Cơ quan nào có thẩm quyền ban hành văn bản, giấy tờ trong lĩnh vực văn hóa, thể thao và du lịch?',
    [
        'Khoản 1 Điều 24 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Giviones ĐẾN Ngày.13.76.12025 trong lĩnh vực văn hóa, thể thao và du lịch Văn bản, giấy tờ đã được cơ quan, người có thẩm quyền ban hành, cấp đang còn hiệu lực hoặc chưa hết thời hạn sử dụng trước khi Nghị định này có hiệu lực thì tiếp tục được sử dụng cho đến khi hết thời hạn ghi trong văn bản, giấy tờ đó.',
        'Tại điểm b Khoản 1 Điều 4 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Người hy sinh thuộc cơ quan cấp xã và các trường hợp không thuộc quy định tại khoản 1, 2, 3,4 Điều 16 Nghị định số 131/2021/NĐ-CP và điểma',
        'Khoản 1 Điều 6 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Tổ chức quản lý, phát triển chăn nuôi tại địa phương; thống kê, đánh tại điểm c khoản 2 Điều 80 Luật Chăn nuôi.',
        'Khoản 3 Điều 16 NGHỊ ĐỊNH Ngày.13.1.6.2025 Quy định về phân quyền, phân cấp; phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực công tác dân tộc, tín ngưỡng, tôn giáo - Căn cứ Luật Tổ chức Chính phủ năm 2025; Trình tự, thủ tục tiếp nhận thông báo danh mục hoạt động tôn giáo quy định tại Mục XI Phụ lục I Nghị định này.',
        'Khoản 3 Điều 11 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp, phân quyền, phân cấp trong lĩnh vực quy hoạch đô thị và nông thôn Gi ĐẾN Ngày. 13-16-12925 - Căn cứ Luật Tổ chức Chính phủ 2025; Không tổ chức lập, phê duyệt nhiệm vụ quy hoạch, quy hoạch đô thị và nông thôn đối với đô thị mới có phạm vi quy hoạch liên quan đến địa giới hành chính của từ 02 tỉnh trở lên theo quy định tại điểm a khoản 1 Điều 17 và điểm a khoản 1 điều 41.',
    ]
)
# [{'corpus_id': ..., 'score': ...}, {'corpus_id': ..., 'score': ...}, ...]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

## Evaluation

### Metrics

#### Cross Encoder Binary Classification

* Dataset: `dev`
* Evaluated with [<code>CEBinaryClassificationEvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CEBinaryClassificationEvaluator)

| Metric                | Value      |
|:----------------------|:-----------|
| accuracy              | 0.8915     |
| accuracy_threshold    | 1.5841     |
| f1                    | 0.8887     |
| f1_threshold          | -0.1877    |
| precision             | 0.8307     |
| recall                | 0.9555     |
| **average_precision** | **0.9522** |

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 13,230 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                                      | sentence_1                                                                                       | label                                                          |
  |:--------|:------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                                          | string                                                                                           | float                                                          |
  | details | <ul><li>min: 26 characters</li><li>mean: 74.07 characters</li><li>max: 211 characters</li></ul> | <ul><li>min: 95 characters</li><li>mean: 475.6 characters</li><li>max: 1725 characters</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.53</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                    | sentence_1                                                                                                                                                                                                                                                                                                                                                                                   | label            |
  |:--------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Cơ quan nào có thẩm quyền ban hành văn bản, giấy tờ trong lĩnh vực văn hóa, thể thao và du lịch?</code> | <code>Khoản 1 Điều 24 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Giviones ĐẾN Ngày.13.76.12025 trong lĩnh vực văn hóa, thể thao và du lịch Văn bản, giấy tờ đã được cơ quan, người có thẩm quyền ban hành, cấp đang còn hiệu lực hoặc chưa hết thời hạn sử dụng trước khi Nghị định này có hiệu lực thì tiếp tục được sử dụng cho đến khi hết thời hạn ghi trong văn bản, giấy tờ đó.</code> | <code>1.0</code> |
  | <code>Điểm b Khoản 1 Điều 4 quy định về điều kiện gì?</code>                                                  | <code>Tại điểm b Khoản 1 Điều 4 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Người hy sinh thuộc cơ quan cấp xã và các trường hợp không thuộc quy định tại khoản 1, 2, 3,4 Điều 16 Nghị định số 131/2021/NĐ-CP và điểma</code>                                                                                | <code>1.0</code> |
  | <code>Quỹ phòng, chống thiên tai được thành lập và quản lý như thế nào theo Nghị định này?</code>             | <code>Khoản 1 Điều 6 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Tổ chức quản lý, phát triển chăn nuôi tại địa phương; thống kê, đánh tại điểm c khoản 2 Điều 80 Luật Chăn nuôi.</code>                                                                                                       | <code>0.0</code> |
* Loss: [<code>BinaryCrossEntropyLoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#binarycrossentropyloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity",
      "pos_weight": null
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 32
- `fp16`: True
- `per_device_eval_batch_size`: 32

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 32
- `num_train_epochs`: 3
- `max_steps`: -1
- `learning_rate`: 5e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0
- `optim`: adamw_torch
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1
- `label_smoothing_factor`: 0.0
- `bf16`: False
- `fp16`: True
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: trackio
- `eval_strategy`: no
- `per_device_eval_batch_size`: 32
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 42
- `data_seed`: None
- `use_cpu`: False
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: []
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss | dev_average_precision |
|:------:|:----:|:-------------:|:---------------------:|
| 1.0    | 414  | -             | 0.9425                |
| 1.2077 | 500  | 0.3943        | -                     |
| 2.0    | 828  | -             | 0.9506                |
| 2.4155 | 1000 | 0.2558        | -                     |
| 3.0    | 1242 | -             | 0.9522                |


### Framework Versions
- Python: 3.11.14
- Sentence Transformers: 5.2.3
- Transformers: 5.2.0
- PyTorch: 2.5.1+cu121
- Accelerate: 1.12.0
- Datasets: 4.5.0
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->