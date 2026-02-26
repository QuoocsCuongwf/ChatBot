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
      name: v6 1
      type: v6_1
    metrics:
    - type: accuracy
      value: 0.863
      name: Accuracy
    - type: accuracy_threshold
      value: -0.4904260039329529
      name: Accuracy Threshold
    - type: f1
      value: 0.8647581441263573
      name: F1
    - type: f1_threshold
      value: -0.5211328864097595
      name: F1 Threshold
    - type: precision
      value: 0.8538011695906432
      name: Precision
    - type: recall
      value: 0.876
      name: Recall
    - type: average_precision
      value: 0.9419176636969666
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
    ['Việc cấp giấy chứng nhận đăng ký cung cấp dịch vụ viễn thông do ai thực hiện?', 'Khoản 1 Điều 20 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp trong lĩnh vực Gi3: ĐẾN quản lý nhà nước của Bộ Khoa học và Công nghệ Ngày 45161.2025 Việc cấp giấy chứng nhận đăng ký cung cấp dịch vụ viễn thông theo quy định tại khoản 4 Điều 44 Nghị định số 163/2024/NĐ-CP do Ủy ban nhân dân cấp tỉnh nơi doanh nghiệp đặt trụ sở chính thực hiện.'],
    ['Nơi nào quy định về tổ chức đánh giá và lấy ý kiến công nhận xã đạt chuẩn nông thôn mới?', 'Khoản 1 Điều 44 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Tổ chức đánh giá, lấy ý kiến, hoàn thiện hồ sơ xét thu hồi quyết định công nhận xã đạt chuẩn nông thôn mới, xã đạt Chuẩn nông thôn Mới nâng cao, xã đạt chuẩn nông thôn mới kiểu mẫu theo quy định tại Điều 23, khoản 1 Điều 24 của Quy định điều kiện, trình tự, thủ tục, hồ sơ xét, công nhận, công bố và thu hồi quyết định công nhận địa phương đạt chuẩn nông thôn mới, đạt chuẩn Nông thôn mới nâng cao, đạt chuẩn nông thôn mới kiểu mẫu và hoàn thành nhiệm vụ xây dựng nông thôn mới giai đoạn 1021 - 2025 ban hành kèm theo Quyết định số 18/2022/QĐ-TTg ngày 02 tháng 8 năm 2021 của Thủ tướng Chính phủ.'],
    ['Phân định thẩm quyền giữa hai cấp chính quyền địa phương trong lĩnh vực nào được quy định tại Khoản 6 Điều 2?', 'Khoản 2 Điều 42 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của bộ tài chính - Nhiệm vụ, quyền hạn của Chủ tịch Ủy ban nhân dân cấp huyện được quy định tại khoản 1 Điều 26 Nghị định số 78/2002/NĐ-CP do Chủ tịch Ủy ban nhân dân cấp xã thực hiện.'],
    ['Việc định giá tài sản khi cưỡng chế bằng biện pháp kê biên tài sản do ai thực hiện?', 'Khoản 2 Điều 8 NGHỊ ĐỊNH Quy định tổ chức các cơ quan chuyên môn thuộc Ủy ban nhân dân tỉnh, thành phố trực thuộc trung ương và Ủy ban nhân dân xã, phường, đặc khu thuộc tỉnh, thành phố trực thuộc trung ương G13:.. ĐẾN - Căn cứ Luật Tổ chức Chính phủ năm 2025; Sở Tư pháp Tham mưu, giúp Ủy ban nhân dân cấp tỉnh thực hiện chức năng quản lý nhà nước về: Công tác xây dựng và tổ chức thi hành pháp luật, theo dõi việc thi hành văn bản quy phạm pháp luật, kiểm tra, xử lý văn bản Quy phạm pháp Luật; phổ biến, giáo dục pháp luật, hòa giải ở cơ sở, hộ tịch, quốc tịch; nuôi con nuôi; luật sư, tư vấn pháp luật, trợ giúp pháp lý, công chứng, chứng thực, giám định tư pháp, đấu giá tài sản, trọng tài thương mại, hòa giải thương mại. quản tài viên, doanh nghiệp quản lý, thanh lý tài sản và hoạt động hành nghề quản lý; thanh lý tài sản, thừa phát lại, đăng ký biện pháp bảo đảm, bồi thường nhà nước; pháp chế, quản lý công tác thi hành pháp luật về xử lý vi phạm hành chính và công tác tư pháp khác theo quy định của pháp luật.'],
    ['Các giấy tờ cần có khi hưởng trợ cấp tuất nuôi dưỡng hằng tháng là gì?', 'Theo Điều 32 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Thủ tục hưởng trợ cấp một lần khi người có công đang hưởng trợ cấp ưu đãi từ trần Thủ tục hưởng Trợ cấp một lần khi người có công đang hưởng trợ cấp ưu đãi từ trần quy định tại khoản 2, khoản 3 Điều 123 Nghị định 131/2021/NĐ-CP thực hiện như sau: Ủy ban nhân dân cấp xã trong thời gian 07 ngày làm việc kể từ ngày nhận đủ các giấy tờ, có trách nhiệm xác nhận bản khai và lập danh sách gửi Sở Nội vụ theo quy định.'],
]
scores = model.predict(pairs)
print(scores.shape)
# (5,)

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'Việc cấp giấy chứng nhận đăng ký cung cấp dịch vụ viễn thông do ai thực hiện?',
    [
        'Khoản 1 Điều 20 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp trong lĩnh vực Gi3: ĐẾN quản lý nhà nước của Bộ Khoa học và Công nghệ Ngày 45161.2025 Việc cấp giấy chứng nhận đăng ký cung cấp dịch vụ viễn thông theo quy định tại khoản 4 Điều 44 Nghị định số 163/2024/NĐ-CP do Ủy ban nhân dân cấp tỉnh nơi doanh nghiệp đặt trụ sở chính thực hiện.',
        'Khoản 1 Điều 44 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Tổ chức đánh giá, lấy ý kiến, hoàn thiện hồ sơ xét thu hồi quyết định công nhận xã đạt chuẩn nông thôn mới, xã đạt Chuẩn nông thôn Mới nâng cao, xã đạt chuẩn nông thôn mới kiểu mẫu theo quy định tại Điều 23, khoản 1 Điều 24 của Quy định điều kiện, trình tự, thủ tục, hồ sơ xét, công nhận, công bố và thu hồi quyết định công nhận địa phương đạt chuẩn nông thôn mới, đạt chuẩn Nông thôn mới nâng cao, đạt chuẩn nông thôn mới kiểu mẫu và hoàn thành nhiệm vụ xây dựng nông thôn mới giai đoạn 1021 - 2025 ban hành kèm theo Quyết định số 18/2022/QĐ-TTg ngày 02 tháng 8 năm 2021 của Thủ tướng Chính phủ.',
        'Khoản 2 Điều 42 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của bộ tài chính - Nhiệm vụ, quyền hạn của Chủ tịch Ủy ban nhân dân cấp huyện được quy định tại khoản 1 Điều 26 Nghị định số 78/2002/NĐ-CP do Chủ tịch Ủy ban nhân dân cấp xã thực hiện.',
        'Khoản 2 Điều 8 NGHỊ ĐỊNH Quy định tổ chức các cơ quan chuyên môn thuộc Ủy ban nhân dân tỉnh, thành phố trực thuộc trung ương và Ủy ban nhân dân xã, phường, đặc khu thuộc tỉnh, thành phố trực thuộc trung ương G13:.. ĐẾN - Căn cứ Luật Tổ chức Chính phủ năm 2025; Sở Tư pháp Tham mưu, giúp Ủy ban nhân dân cấp tỉnh thực hiện chức năng quản lý nhà nước về: Công tác xây dựng và tổ chức thi hành pháp luật, theo dõi việc thi hành văn bản quy phạm pháp luật, kiểm tra, xử lý văn bản Quy phạm pháp Luật; phổ biến, giáo dục pháp luật, hòa giải ở cơ sở, hộ tịch, quốc tịch; nuôi con nuôi; luật sư, tư vấn pháp luật, trợ giúp pháp lý, công chứng, chứng thực, giám định tư pháp, đấu giá tài sản, trọng tài thương mại, hòa giải thương mại. quản tài viên, doanh nghiệp quản lý, thanh lý tài sản và hoạt động hành nghề quản lý; thanh lý tài sản, thừa phát lại, đăng ký biện pháp bảo đảm, bồi thường nhà nước; pháp chế, quản lý công tác thi hành pháp luật về xử lý vi phạm hành chính và công tác tư pháp khác theo quy định của pháp luật.',
        'Theo Điều 32 NGHỊ ĐỊNH "Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nội vụ Thủ tục hưởng trợ cấp một lần khi người có công đang hưởng trợ cấp ưu đãi từ trần Thủ tục hưởng Trợ cấp một lần khi người có công đang hưởng trợ cấp ưu đãi từ trần quy định tại khoản 2, khoản 3 Điều 123 Nghị định 131/2021/NĐ-CP thực hiện như sau: Ủy ban nhân dân cấp xã trong thời gian 07 ngày làm việc kể từ ngày nhận đủ các giấy tờ, có trách nhiệm xác nhận bản khai và lập danh sách gửi Sở Nội vụ theo quy định.',
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

* Dataset: `v6_1`
* Evaluated with [<code>CEBinaryClassificationEvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CEBinaryClassificationEvaluator)

| Metric                | Value      |
|:----------------------|:-----------|
| accuracy              | 0.863      |
| accuracy_threshold    | -0.4904    |
| f1                    | 0.8648     |
| f1_threshold          | -0.5211    |
| precision             | 0.8538     |
| recall                | 0.876      |
| **average_precision** | **0.9419** |

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
  | details | <ul><li>min: 27 characters</li><li>mean: 74.13 characters</li><li>max: 215 characters</li></ul> | <ul><li>min: 152 characters</li><li>mean: 501.43 characters</li><li>max: 1725 characters</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.34</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                 | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | label            |
  |:---------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Việc cấp giấy chứng nhận đăng ký cung cấp dịch vụ viễn thông do ai thực hiện?</code>                                 | <code>Khoản 1 Điều 20 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp trong lĩnh vực Gi3: ĐẾN quản lý nhà nước của Bộ Khoa học và Công nghệ Ngày 45161.2025 Việc cấp giấy chứng nhận đăng ký cung cấp dịch vụ viễn thông theo quy định tại khoản 4 Điều 44 Nghị định số 163/2024/NĐ-CP do Ủy ban nhân dân cấp tỉnh nơi doanh nghiệp đặt trụ sở chính thực hiện.</code>                                                                                                                                                                                                                                                                                                                                                                                                                            | <code>1.0</code> |
  | <code>Nơi nào quy định về tổ chức đánh giá và lấy ý kiến công nhận xã đạt chuẩn nông thôn mới?</code>                      | <code>Khoản 1 Điều 44 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Tổ chức đánh giá, lấy ý kiến, hoàn thiện hồ sơ xét thu hồi quyết định công nhận xã đạt chuẩn nông thôn mới, xã đạt Chuẩn nông thôn Mới nâng cao, xã đạt chuẩn nông thôn mới kiểu mẫu theo quy định tại Điều 23, khoản 1 Điều 24 của Quy định điều kiện, trình tự, thủ tục, hồ sơ xét, công nhận, công bố và thu hồi quyết định công nhận địa phương đạt chuẩn nông thôn mới, đạt chuẩn Nông thôn mới nâng cao, đạt chuẩn nông thôn mới kiểu mẫu và hoàn thành nhiệm vụ xây dựng nông thôn mới giai đoạn 1021 - 2025 ban hành kèm theo Quyết định số 18/2022/QĐ-TTg ngày 02 tháng 8 năm 2021 của Thủ tướng Chính phủ.</code> | <code>1.0</code> |
  | <code>Phân định thẩm quyền giữa hai cấp chính quyền địa phương trong lĩnh vực nào được quy định tại Khoản 6 Điều 2?</code> | <code>Khoản 2 Điều 42 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của bộ tài chính - Nhiệm vụ, quyền hạn của Chủ tịch Ủy ban nhân dân cấp huyện được quy định tại khoản 1 Điều 26 Nghị định số 78/2002/NĐ-CP do Chủ tịch Ủy ban nhân dân cấp xã thực hiện.</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                           | <code>0.0</code> |
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
| Epoch  | Step | Training Loss | v6_1_average_precision |
|:------:|:----:|:-------------:|:----------------------:|
| 0.8052 | 500  | 0.6295        | -                      |
| 1.0    | 621  | -             | 0.9075                 |
| 1.6103 | 1000 | 0.3629        | -                      |
| 2.0    | 1242 | -             | 0.9296                 |
| 2.4155 | 1500 | 0.3178        | -                      |
| 3.0    | 1863 | -             | 0.9387                 |
| 3.2206 | 2000 | 0.2861        | -                      |
| 4.0    | 2484 | -             | 0.9404                 |
| 4.0258 | 2500 | 0.2722        | -                      |
| 4.8309 | 3000 | 0.2506        | -                      |
| 5.0    | 3105 | -             | 0.9419                 |


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