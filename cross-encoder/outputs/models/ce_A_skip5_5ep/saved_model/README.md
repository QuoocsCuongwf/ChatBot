---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:19845
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
      name: A skip5
      type: A_skip5
    metrics:
    - type: accuracy
      value: 0.797
      name: Accuracy
    - type: accuracy_threshold
      value: -0.12806883454322815
      name: Accuracy Threshold
    - type: f1
      value: 0.8054298642533936
      name: F1
    - type: f1_threshold
      value: -1.0961594581604004
      name: F1 Threshold
    - type: precision
      value: 0.7355371900826446
      name: Precision
    - type: recall
      value: 0.89
      name: Recall
    - type: average_precision
      value: 0.8860172214457936
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
    ['Ai thực hiện thẩm quyền lập phương án xử lý tài sản của Phòng Tài chính - Kế hoạch cấp huyện?', 'Tại điểm a Khoản 7 Điều 20 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của bộ tài chính - Làm đơn vị chủ trì quản lý tài sản đối với tài sản do cơ quan thi hành án định tại khoản 2 Điều 5 Nghị định số 77/2025/NĐ-CP, tài sản vô chủ, tài Sản bị đánh rơi, bỏ quên, di sản không có người thừa kế của Phòng Tài chính - Kế hoạch cấp huyện được quy định tại khoản 4 Điều 5 Nghị định số 77/2025/NĐ-CP;'],
    ['Nhiệm vụ quản lý nhà nước về quỹ xã hội, quỹ từ thiện được phân cấp đến đâu?', 'Khoản 5 Điều 58 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Hàng năm, tổng hợp, báo cáo Ủy ban nhân dân cấp tỉnh về tình hình tổ chức, hoạt động và quản lý quỹ hoạt động trong phạm vi xã.'],
    ['Việc bổ nhiệm lại Thừa phát lại quy định ở đâu?', 'Khoản 1 Điều 16 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Cử Ngày 13.16.12025 trong lĩnh vực quản lý nhà nước của Bộ Tư pháp Việc bổ nhiệm lại công chứng viên được quy định tại khoản 4 Điều 17 của Luật Công chứng, Điều 7 của Nghị định số 104/2025/NĐ-CP thuộc thẩm quyền của Chủ tịch Ủy ban nhân dân cấp tỉnh.'],
    ['Lý do để phát huy tính chủ động, sáng tạo trong quản lý nhà nước về văn hóa, thể thao và du lịch là gì?', 'Khoản 2 Điều 2 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Giviones ĐẾN Ngày.13.76.12025 trong lĩnh vực văn hóa, thể thao và du lịch Bảo đảm phân cấp triệt để các nhiệm vụ giữa cơ quan nhà nước ở trung ương với chính quyền địa phương, bảo đảm thẩm quyền quản lý thống nhất của Chính phủ, quyền điều hành của người đứng đầu Chính phủ đối với lĩnh vực quản lý nhà nước về văn hóa, thể thao và du lịch; phát huy tính chủ động, sáng quản lý nhà nước trong lĩnh vực văn hóa, thể thao và du lịch.'],
    ['Nghị định nào quy định chi tiết về việc thi hành Luật Tài nguyên nước?', 'Khoản 7 Điều 22 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Phối hợp với tổ chức quản lý, vận hành hồ chứa thủy điện thực hiện giới từ Uỷ ban nhân dân cấp tỉnh để quản lý, bảo vệ theo quy định tại khoản 5 Điều 28 Nghị định số 53/2024/NĐ-CP ngày 16 tháng 5 năm 202 4 của Chính phủ quy định chi tiết thi hành một số điều của Luật Tài nguyên nước.'],
]
scores = model.predict(pairs)
print(scores.shape)
# (5,)

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'Ai thực hiện thẩm quyền lập phương án xử lý tài sản của Phòng Tài chính - Kế hoạch cấp huyện?',
    [
        'Tại điểm a Khoản 7 Điều 20 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của bộ tài chính - Làm đơn vị chủ trì quản lý tài sản đối với tài sản do cơ quan thi hành án định tại khoản 2 Điều 5 Nghị định số 77/2025/NĐ-CP, tài sản vô chủ, tài Sản bị đánh rơi, bỏ quên, di sản không có người thừa kế của Phòng Tài chính - Kế hoạch cấp huyện được quy định tại khoản 4 Điều 5 Nghị định số 77/2025/NĐ-CP;',
        'Khoản 5 Điều 58 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Hàng năm, tổng hợp, báo cáo Ủy ban nhân dân cấp tỉnh về tình hình tổ chức, hoạt động và quản lý quỹ hoạt động trong phạm vi xã.',
        'Khoản 1 Điều 16 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Cử Ngày 13.16.12025 trong lĩnh vực quản lý nhà nước của Bộ Tư pháp Việc bổ nhiệm lại công chứng viên được quy định tại khoản 4 Điều 17 của Luật Công chứng, Điều 7 của Nghị định số 104/2025/NĐ-CP thuộc thẩm quyền của Chủ tịch Ủy ban nhân dân cấp tỉnh.',
        'Khoản 2 Điều 2 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Giviones ĐẾN Ngày.13.76.12025 trong lĩnh vực văn hóa, thể thao và du lịch Bảo đảm phân cấp triệt để các nhiệm vụ giữa cơ quan nhà nước ở trung ương với chính quyền địa phương, bảo đảm thẩm quyền quản lý thống nhất của Chính phủ, quyền điều hành của người đứng đầu Chính phủ đối với lĩnh vực quản lý nhà nước về văn hóa, thể thao và du lịch; phát huy tính chủ động, sáng quản lý nhà nước trong lĩnh vực văn hóa, thể thao và du lịch.',
        'Khoản 7 Điều 22 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Phối hợp với tổ chức quản lý, vận hành hồ chứa thủy điện thực hiện giới từ Uỷ ban nhân dân cấp tỉnh để quản lý, bảo vệ theo quy định tại khoản 5 Điều 28 Nghị định số 53/2024/NĐ-CP ngày 16 tháng 5 năm 202 4 của Chính phủ quy định chi tiết thi hành một số điều của Luật Tài nguyên nước.',
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

* Dataset: `A_skip5`
* Evaluated with [<code>CEBinaryClassificationEvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CEBinaryClassificationEvaluator)

| Metric                | Value     |
|:----------------------|:----------|
| accuracy              | 0.797     |
| accuracy_threshold    | -0.1281   |
| f1                    | 0.8054    |
| f1_threshold          | -1.0962   |
| precision             | 0.7355    |
| recall                | 0.89      |
| **average_precision** | **0.886** |

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

* Size: 19,845 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                                      | sentence_1                                                                                         | label                                                          |
  |:--------|:------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                                          | string                                                                                             | float                                                          |
  | details | <ul><li>min: 23 characters</li><li>mean: 75.07 characters</li><li>max: 192 characters</li></ul> | <ul><li>min: 145 characters</li><li>mean: 463.23 characters</li><li>max: 1564 characters</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.32</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                 | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | label            |
  |:-----------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Ai thực hiện thẩm quyền lập phương án xử lý tài sản của Phòng Tài chính - Kế hoạch cấp huyện?</code> | <code>Tại điểm a Khoản 7 Điều 20 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của bộ tài chính - Làm đơn vị chủ trì quản lý tài sản đối với tài sản do cơ quan thi hành án định tại khoản 2 Điều 5 Nghị định số 77/2025/NĐ-CP, tài sản vô chủ, tài Sản bị đánh rơi, bỏ quên, di sản không có người thừa kế của Phòng Tài chính - Kế hoạch cấp huyện được quy định tại khoản 4 Điều 5 Nghị định số 77/2025/NĐ-CP;</code> | <code>0.0</code> |
  | <code>Nhiệm vụ quản lý nhà nước về quỹ xã hội, quỹ từ thiện được phân cấp đến đâu?</code>                  | <code>Khoản 5 Điều 58 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Hàng năm, tổng hợp, báo cáo Ủy ban nhân dân cấp tỉnh về tình hình tổ chức, hoạt động và quản lý quỹ hoạt động trong phạm vi xã.</code>                                                                                                                                                                                                | <code>0.0</code> |
  | <code>Việc bổ nhiệm lại Thừa phát lại quy định ở đâu?</code>                                               | <code>Khoản 1 Điều 16 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Cử Ngày 13.16.12025 trong lĩnh vực quản lý nhà nước của Bộ Tư pháp Việc bổ nhiệm lại công chứng viên được quy định tại khoản 4 Điều 17 của Luật Công chứng, Điều 7 của Nghị định số 104/2025/NĐ-CP thuộc thẩm quyền của Chủ tịch Ủy ban nhân dân cấp tỉnh.</code>                                                                                                                                                      | <code>0.0</code> |
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
- `num_train_epochs`: 5
- `fp16`: True
- `per_device_eval_batch_size`: 32

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 32
- `num_train_epochs`: 5
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
| Epoch  | Step | Training Loss | A_skip5_average_precision |
|:------:|:----:|:-------------:|:-------------------------:|
| 0.8052 | 500  | 0.6703        | -                         |
| 1.0    | 621  | -             | 0.8309                    |
| 1.6103 | 1000 | 0.4437        | -                         |
| 2.0    | 1242 | -             | 0.8628                    |
| 2.4155 | 1500 | 0.4055        | -                         |
| 3.0    | 1863 | -             | 0.8811                    |
| 3.2206 | 2000 | 0.3793        | -                         |
| 4.0    | 2484 | -             | 0.8811                    |
| 4.0258 | 2500 | 0.3558        | -                         |
| 4.8309 | 3000 | 0.3451        | -                         |
| 5.0    | 3105 | -             | 0.8860                    |


### Framework Versions
- Python: 3.11.14
- Sentence Transformers: 5.2.3
- Transformers: 5.2.0
- PyTorch: 2.6.0+cu124
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