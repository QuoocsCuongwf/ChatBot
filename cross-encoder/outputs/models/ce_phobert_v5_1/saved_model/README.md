---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:19845
- loss:BinaryCrossEntropyLoss
base_model: vinai/phobert-base
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
- name: CrossEncoder based on vinai/phobert-base
  results:
  - task:
      type: cross-encoder-binary-classification
      name: Cross Encoder Binary Classification
    dataset:
      name: dev v5 1
      type: dev_v5_1
    metrics:
    - type: accuracy
      value: 0.903
      name: Accuracy
    - type: accuracy_threshold
      value: 0.39537835121154785
      name: Accuracy Threshold
    - type: f1
      value: 0.9054054054054054
      name: F1
    - type: f1_threshold
      value: 0.10645975172519684
      name: F1 Threshold
    - type: precision
      value: 0.875
      name: Precision
    - type: recall
      value: 0.938
      name: Recall
    - type: average_precision
      value: 0.9726660181693116
      name: Average Precision
---

# CrossEncoder based on vinai/phobert-base

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model finetuned from [vinai/phobert-base](https://huggingface.co/vinai/phobert-base) using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
- **Base model:** [vinai/phobert-base](https://huggingface.co/vinai/phobert-base) <!-- at revision c1e37c5c86f918761049cef6fa216b4779d0d01d -->
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
    ['Ủy ban nhân dân cấp xã cần phối hợp với ai trong quá trình xây dựng kế hoạch phát triển nhà ở?', 'Tại điểm c Khoản 2 Điều 11 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương cổng thông tin điện tử chính phủ 192 cấp trong lĩnh vực quản lý nhà nước của Bộ Xây dựng ĐẾN Ngày. 13.1.67.2025 Trong quá trình xây dựng kế hoạch phát triển nhà ở, Ủy ban nhân dân cấp xã và các cơ quan có liên quan của địa phương có trách nhiệm phối hợp với cơ quan quản lý nhà ở cấp tỉnh, đơn vị tư vấn để tổ chức khảo sát, tổng hợp, cung cấp số liệu, xây dựng kế hoạch phát triển nhà ở, trường hợp trong kế hoạch có sử dụng vốn đầu tư công để thực hiện các dự án đầu tư xây dựng nhà ở thì trong nội dung phải nêu cụ thể danh mục dự án có sử dụng vốn, số vốn cần bố trí, giai đoạn giải ngân trong kỳ kế hoạch để lấy ý kiến của cơ quan quản lý chuyên ngành của tỉnh; "tháng'],
    ['Ai thực hiện thẩm quyền quyết định cấp giấy phép cho văn phòng đại diện?', 'Khoản 1 Điều 31 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Cử Ngày 13.16.12025 trong lĩnh vực quản lý nhà nước của Bộ Tư pháp Việc thay đổi nội dung Giấy phép thành lập Trung tâm trọng tài, Giấy đăng ký hoạt động của Trung tâm trọng tài trong trường hợp thay đổi người đại diện theo pháp luật, địa điểm đặt trụ sở được quy định tại khoản 2 Điều 11 của Nghị định số 63/2011/NĐ-CP thuộc thẩm quyền của Chủ tịch Ủy ban nhân dân cấp tỉnh.'],
    ['Thủ tục xóa tên tổ chức đại diện sở hữu công nghiệp như thế nào?', 'Khoản 2 Điều 7 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp trong lĩnh vực Gi3: ĐẾN quản lý nhà nước của Bộ Khoa học và Công nghệ Ngày 45161.2025 Trình tự, thủ tục xóa tên tổ chức dịch vụ đại diện sở hữu công nghiệp được quy định tại Mục I và khoản 7 Mục II Phụ lục III.1 ban hành kèm theo Nghị định này'],
    ['Các sở, ban, ngành trực thuộc Ủy ban nhân dân cấp tỉnh làm gì theo quy định tại khoản 1 Điều 100 Luật Giao thông đường thủy nội địa năm 2004?', 'Khoản 1 Điều 27 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương cổng thông tin điện tử chính phủ 192 cấp trong lĩnh vực quản lý nhà nước của Bộ Xây dựng ĐẾN Ngày. 13.1.67.2025 Ủy ban nhân dân cấp tỉnh tổ chức, chỉ đạo các sở, ban, ngành trực thuộc và Ủy ban nhân dân cấp xã thực hiện trách nhiệm quản lý hoạt động đường thủy nội địa theo quy định tại khoản 1 Điều 100 Luật Giao thông đường thủy nội địa năm 2004 (đã được sửa đổi, bổ sung năm 2214).'],
    ['Nội vụ thuộc Ủy ban nhân dân cấp xã thực hiện theo quy định nào?', 'Theo Điều 76 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Quản lý hòa giải viên lao động viên lao động thuộc Sở Nội vụ và cơ quan chuyên môn thực hiện nhiệm vụ về lĩnh vực nội vụ thuộc Ủy ban nhân dân cấp xã theo quy định tại điểm b khoản 2 Điều 97 Nghị định số 145/2020/NĐ-CP. nội vụ thuộc Ủy ban nhân dân cấp xã theo quy định tại khoản 4 Điều 97 Nghị định số 145/2020/NĐ-CP:'],
]
scores = model.predict(pairs)
print(scores.shape)
# (5,)

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'Ủy ban nhân dân cấp xã cần phối hợp với ai trong quá trình xây dựng kế hoạch phát triển nhà ở?',
    [
        'Tại điểm c Khoản 2 Điều 11 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương cổng thông tin điện tử chính phủ 192 cấp trong lĩnh vực quản lý nhà nước của Bộ Xây dựng ĐẾN Ngày. 13.1.67.2025 Trong quá trình xây dựng kế hoạch phát triển nhà ở, Ủy ban nhân dân cấp xã và các cơ quan có liên quan của địa phương có trách nhiệm phối hợp với cơ quan quản lý nhà ở cấp tỉnh, đơn vị tư vấn để tổ chức khảo sát, tổng hợp, cung cấp số liệu, xây dựng kế hoạch phát triển nhà ở, trường hợp trong kế hoạch có sử dụng vốn đầu tư công để thực hiện các dự án đầu tư xây dựng nhà ở thì trong nội dung phải nêu cụ thể danh mục dự án có sử dụng vốn, số vốn cần bố trí, giai đoạn giải ngân trong kỳ kế hoạch để lấy ý kiến của cơ quan quản lý chuyên ngành của tỉnh; "tháng',
        'Khoản 1 Điều 31 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Cử Ngày 13.16.12025 trong lĩnh vực quản lý nhà nước của Bộ Tư pháp Việc thay đổi nội dung Giấy phép thành lập Trung tâm trọng tài, Giấy đăng ký hoạt động của Trung tâm trọng tài trong trường hợp thay đổi người đại diện theo pháp luật, địa điểm đặt trụ sở được quy định tại khoản 2 Điều 11 của Nghị định số 63/2011/NĐ-CP thuộc thẩm quyền của Chủ tịch Ủy ban nhân dân cấp tỉnh.',
        'Khoản 2 Điều 7 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp trong lĩnh vực Gi3: ĐẾN quản lý nhà nước của Bộ Khoa học và Công nghệ Ngày 45161.2025 Trình tự, thủ tục xóa tên tổ chức dịch vụ đại diện sở hữu công nghiệp được quy định tại Mục I và khoản 7 Mục II Phụ lục III.1 ban hành kèm theo Nghị định này',
        'Khoản 1 Điều 27 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương cổng thông tin điện tử chính phủ 192 cấp trong lĩnh vực quản lý nhà nước của Bộ Xây dựng ĐẾN Ngày. 13.1.67.2025 Ủy ban nhân dân cấp tỉnh tổ chức, chỉ đạo các sở, ban, ngành trực thuộc và Ủy ban nhân dân cấp xã thực hiện trách nhiệm quản lý hoạt động đường thủy nội địa theo quy định tại khoản 1 Điều 100 Luật Giao thông đường thủy nội địa năm 2004 (đã được sửa đổi, bổ sung năm 2214).',
        'Theo Điều 76 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Quản lý hòa giải viên lao động viên lao động thuộc Sở Nội vụ và cơ quan chuyên môn thực hiện nhiệm vụ về lĩnh vực nội vụ thuộc Ủy ban nhân dân cấp xã theo quy định tại điểm b khoản 2 Điều 97 Nghị định số 145/2020/NĐ-CP. nội vụ thuộc Ủy ban nhân dân cấp xã theo quy định tại khoản 4 Điều 97 Nghị định số 145/2020/NĐ-CP:',
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

* Dataset: `dev_v5_1`
* Evaluated with [<code>CEBinaryClassificationEvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CEBinaryClassificationEvaluator)

| Metric                | Value      |
|:----------------------|:-----------|
| accuracy              | 0.903      |
| accuracy_threshold    | 0.3954     |
| f1                    | 0.9054     |
| f1_threshold          | 0.1065     |
| precision             | 0.875      |
| recall                | 0.938      |
| **average_precision** | **0.9727** |

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
  | details | <ul><li>min: 23 characters</li><li>mean: 75.47 characters</li><li>max: 215 characters</li></ul> | <ul><li>min: 145 characters</li><li>mean: 473.06 characters</li><li>max: 2110 characters</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.32</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                  | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | label            |
  |:------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Ủy ban nhân dân cấp xã cần phối hợp với ai trong quá trình xây dựng kế hoạch phát triển nhà ở?</code> | <code>Tại điểm c Khoản 2 Điều 11 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương cổng thông tin điện tử chính phủ 192 cấp trong lĩnh vực quản lý nhà nước của Bộ Xây dựng ĐẾN Ngày. 13.1.67.2025 Trong quá trình xây dựng kế hoạch phát triển nhà ở, Ủy ban nhân dân cấp xã và các cơ quan có liên quan của địa phương có trách nhiệm phối hợp với cơ quan quản lý nhà ở cấp tỉnh, đơn vị tư vấn để tổ chức khảo sát, tổng hợp, cung cấp số liệu, xây dựng kế hoạch phát triển nhà ở, trường hợp trong kế hoạch có sử dụng vốn đầu tư công để thực hiện các dự án đầu tư xây dựng nhà ở thì trong nội dung phải nêu cụ thể danh mục dự án có sử dụng vốn, số vốn cần bố trí, giai đoạn giải ngân trong kỳ kế hoạch để lấy ý kiến của cơ quan quản lý chuyên ngành của tỉnh; "tháng</code> | <code>1.0</code> |
  | <code>Ai thực hiện thẩm quyền quyết định cấp giấy phép cho văn phòng đại diện?</code>                       | <code>Khoản 1 Điều 31 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp Cử Ngày 13.16.12025 trong lĩnh vực quản lý nhà nước của Bộ Tư pháp Việc thay đổi nội dung Giấy phép thành lập Trung tâm trọng tài, Giấy đăng ký hoạt động của Trung tâm trọng tài trong trường hợp thay đổi người đại diện theo pháp luật, địa điểm đặt trụ sở được quy định tại khoản 2 Điều 11 của Nghị định số 63/2011/NĐ-CP thuộc thẩm quyền của Chủ tịch Ủy ban nhân dân cấp tỉnh.</code>                                                                                                                                                                                                                                                                                                                                                 | <code>0.0</code> |
  | <code>Thủ tục xóa tên tổ chức đại diện sở hữu công nghiệp như thế nào?</code>                               | <code>Khoản 2 Điều 7 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp trong lĩnh vực Gi3: ĐẾN quản lý nhà nước của Bộ Khoa học và Công nghệ Ngày 45161.2025 Trình tự, thủ tục xóa tên tổ chức dịch vụ đại diện sở hữu công nghiệp được quy định tại Mục I và khoản 7 Mục II Phụ lục III.1 ban hành kèm theo Nghị định này</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | <code>1.0</code> |
* Loss: [<code>BinaryCrossEntropyLoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#binarycrossentropyloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity",
      "pos_weight": null
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 5
- `fp16`: True
- `per_device_eval_batch_size`: 16

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 16
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
- `per_device_eval_batch_size`: 16
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
| Epoch  | Step | Training Loss | dev_v5_1_average_precision |
|:------:|:----:|:-------------:|:--------------------------:|
| 0.4029 | 500  | 0.5676        | -                          |
| 0.8058 | 1000 | 0.3408        | -                          |
| 1.0    | 1241 | -             | 0.9525                     |
| 1.2087 | 1500 | 0.2804        | -                          |
| 1.6116 | 2000 | 0.2477        | -                          |
| 2.0    | 2482 | -             | 0.9653                     |
| 2.0145 | 2500 | 0.2357        | -                          |
| 2.4174 | 3000 | 0.2078        | -                          |
| 2.8203 | 3500 | 0.2040        | -                          |
| 3.0    | 3723 | -             | 0.9677                     |
| 3.2232 | 4000 | 0.1738        | -                          |
| 3.6261 | 4500 | 0.1729        | -                          |
| 4.0    | 4964 | -             | 0.9711                     |
| 4.0290 | 5000 | 0.1696        | -                          |
| 4.4319 | 5500 | 0.1468        | -                          |
| 4.8348 | 6000 | 0.1435        | -                          |
| 5.0    | 6205 | -             | 0.9727                     |


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