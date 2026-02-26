---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:26460
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
      name: dev v5
      type: dev_v5
    metrics:
    - type: accuracy
      value: 0.71
      name: Accuracy
    - type: accuracy_threshold
      value: -0.6320762634277344
      name: Accuracy Threshold
    - type: f1
      value: 0.7473426001635322
      name: F1
    - type: f1_threshold
      value: -1.8709959983825684
      name: F1 Threshold
    - type: precision
      value: 0.632088520055325
      name: Precision
    - type: recall
      value: 0.914
      name: Recall
    - type: average_precision
      value: 0.7656645690236954
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
    ['Việc thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không do ai quyết định?', 'Khoản 3 Điều 6 NGHỊ ĐỊNH Giờ...... ĐẾN Quy định về phân cấp thẩm quyền quản lý nhà nước Ngày 13.16.2025 trong lĩnh vực quản lý, sử dụng tài sản công Bộ trưởng Bộ Xây dựng quyết định thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không quy định tại điểm a Khoản 2 Điều 17, điểm a khoản 12 Điều 18, điểm a khoản 2 Điều 19 Nghị định số 44/2018/NĐ-CP. Trình tự, thủ tục thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không thực hiện theo quy định tại khoản 5 Điều 17, khoản 4 Điều 18, khoản 5 Điều 19 Nghị định số 44/2018/NĐ-CP, không phải thực hiện việc báo cáo Thủ tướng Chính phủ xem xét, quyết định thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không quy định tại điểm b khoản 5 Điều 17, điểm b Khoản 4 Điều 18; điểm b khoản 5 Điều 19 Nghị định số 44/2018/NĐ-CP.'],
    ['Việc lập báo cáo đề xuất chủ trương đầu tư dự án hỗ trợ kết cấu hạ tầng do ai thực hiện?', 'Khoản 8 Điều 12 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương cổng thông tin điện tử chính phủ 192 cấp trong lĩnh vực quản lý nhà nước của Bộ Xây dựng ĐẾN Ngày. 13.1.67.2025 Trách nhiệm tiếp nhận và công khai thông tin về dự án cải tạo, xây dựng lại nhà chung cư, tiếp nhận hồ sơ đăng ký tham gia làm chủ đầu tư dự án, phối hợp với Sở Xây dựng tổ chức lấy ý kiến các chủ sở hữu nhà chung cư, ký xác nhận biên bản lựa chọn chủ đầu tư dự án quy định tại khoản 2, khoản 3, khoản 4 khoản 5 và khoản 6 Điều 17 Nghị định số 98/2024/NĐ-CP ngày 25 tháng 7 năm 2024 của Chính phủ do Ủy ban nhân dân cấp xã thực hiện. phê duyệt phương án bồi thường, hỗ trợ tái định cư quy định khoản 9 Điều 18 Nghị định số 98/2024/NĐ-CP ngày 25 tháng 7 năm 202 4 của Chính phủ do Ủy ban nhân dân cấp xã thực hiện'],
    ['Phương châm của Nghị định này trong việc tiếp cận thông tin là gì?', 'Khoản 7 Điều 2 NGHỊ ĐỊNH Ngày 13.16.12025 Quy định về phân quyền, phân cấp trong lĩnh vực đối ngoại Bảo đảm quyền con người, quyền công dân, bảo đảm công khai, minh bạch, tạo điều kiện thuận lợi cho cá nhân, tổ chức trong việc tiếp cận thông tin, thực hiện các quyền, nghĩa vụ và các thủ tục theo quy định của pháp luật, không làm ảnh hưởng đến hoạt động bình thường của xã hội, người dân, doanh nghiệp.'],
    ['Nghị định nào quy định về việc hành nghề khoan nước dưới đất?', 'Khoản 4 Điều 34 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Quản lý các hoạt động sử dụng các khu vực biển để nuôi trồng thủy sản theo quy định tại Điều 41 Nghị định số 11/2021/NĐ-CP ngày 10 tháng 02 năm 2021 của Chính phủ quy định việc giao các khu vực biển nhất định cho tổ chức; cá nhân có nhu cầu khai thác, sử dụng tài nguyên biển, đã được sửa đổi, bổ sung một số điều tại Nghị định số 65/2025/NĐ-CP ngày 12 tháng 3 năm 2026 của Chính phủ.'],
    ['Doanh nghiệp viễn thông cần có giấy phép gì để triển khai thiết lập mạng viễn thông?', 'Khoản 2 Điều 4 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp trong lĩnh vực Gi3: ĐẾN quản lý nhà nước của Bộ Khoa học và Công nghệ Ngày 45161.2025 Việc cấp, sửa đổi, bổ sung, cấp lại, gia hạn, thu hồi giấy phép cung cấp dịch vụ có hạ tầng mạng, loại mạng viễn thông công cộng cố định mặt đất không sử dụng băng tần số vô tuyến điện không sử dụng số thuê bao viễn thông có phạm vi thiết lập mạng viễn thông trong một tỉnh, thành phố trực thuộc trung ương theo quy định tại khoản 4 Điều 33 Luật Viễn thông do Ủy ban nhân dân cấp tỉnh nơi doanh nghiệp dự kiến hoặc có hoạt động thiết lập mạng viễn thông thực hiện.'],
]
scores = model.predict(pairs)
print(scores.shape)
# (5,)

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'Việc thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không do ai quyết định?',
    [
        'Khoản 3 Điều 6 NGHỊ ĐỊNH Giờ...... ĐẾN Quy định về phân cấp thẩm quyền quản lý nhà nước Ngày 13.16.2025 trong lĩnh vực quản lý, sử dụng tài sản công Bộ trưởng Bộ Xây dựng quyết định thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không quy định tại điểm a Khoản 2 Điều 17, điểm a khoản 12 Điều 18, điểm a khoản 2 Điều 19 Nghị định số 44/2018/NĐ-CP. Trình tự, thủ tục thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không thực hiện theo quy định tại khoản 5 Điều 17, khoản 4 Điều 18, khoản 5 Điều 19 Nghị định số 44/2018/NĐ-CP, không phải thực hiện việc báo cáo Thủ tướng Chính phủ xem xét, quyết định thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không quy định tại điểm b khoản 5 Điều 17, điểm b Khoản 4 Điều 18; điểm b khoản 5 Điều 19 Nghị định số 44/2018/NĐ-CP.',
        'Khoản 8 Điều 12 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương cổng thông tin điện tử chính phủ 192 cấp trong lĩnh vực quản lý nhà nước của Bộ Xây dựng ĐẾN Ngày. 13.1.67.2025 Trách nhiệm tiếp nhận và công khai thông tin về dự án cải tạo, xây dựng lại nhà chung cư, tiếp nhận hồ sơ đăng ký tham gia làm chủ đầu tư dự án, phối hợp với Sở Xây dựng tổ chức lấy ý kiến các chủ sở hữu nhà chung cư, ký xác nhận biên bản lựa chọn chủ đầu tư dự án quy định tại khoản 2, khoản 3, khoản 4 khoản 5 và khoản 6 Điều 17 Nghị định số 98/2024/NĐ-CP ngày 25 tháng 7 năm 2024 của Chính phủ do Ủy ban nhân dân cấp xã thực hiện. phê duyệt phương án bồi thường, hỗ trợ tái định cư quy định khoản 9 Điều 18 Nghị định số 98/2024/NĐ-CP ngày 25 tháng 7 năm 202 4 của Chính phủ do Ủy ban nhân dân cấp xã thực hiện',
        'Khoản 7 Điều 2 NGHỊ ĐỊNH Ngày 13.16.12025 Quy định về phân quyền, phân cấp trong lĩnh vực đối ngoại Bảo đảm quyền con người, quyền công dân, bảo đảm công khai, minh bạch, tạo điều kiện thuận lợi cho cá nhân, tổ chức trong việc tiếp cận thông tin, thực hiện các quyền, nghĩa vụ và các thủ tục theo quy định của pháp luật, không làm ảnh hưởng đến hoạt động bình thường của xã hội, người dân, doanh nghiệp.',
        'Khoản 4 Điều 34 NGHỊ ĐỊNH Quy định phân định thẩm quyền của chính quyền địa phương 02 cấp trong lĩnh vực quản lý nhà nước của Bộ Nông nghiệp và Môi trường Quản lý các hoạt động sử dụng các khu vực biển để nuôi trồng thủy sản theo quy định tại Điều 41 Nghị định số 11/2021/NĐ-CP ngày 10 tháng 02 năm 2021 của Chính phủ quy định việc giao các khu vực biển nhất định cho tổ chức; cá nhân có nhu cầu khai thác, sử dụng tài nguyên biển, đã được sửa đổi, bổ sung một số điều tại Nghị định số 65/2025/NĐ-CP ngày 12 tháng 3 năm 2026 của Chính phủ.',
        'Khoản 2 Điều 4 NGHỊ ĐỊNH Quy định về phân quyền, phân cấp trong lĩnh vực Gi3: ĐẾN quản lý nhà nước của Bộ Khoa học và Công nghệ Ngày 45161.2025 Việc cấp, sửa đổi, bổ sung, cấp lại, gia hạn, thu hồi giấy phép cung cấp dịch vụ có hạ tầng mạng, loại mạng viễn thông công cộng cố định mặt đất không sử dụng băng tần số vô tuyến điện không sử dụng số thuê bao viễn thông có phạm vi thiết lập mạng viễn thông trong một tỉnh, thành phố trực thuộc trung ương theo quy định tại khoản 4 Điều 33 Luật Viễn thông do Ủy ban nhân dân cấp tỉnh nơi doanh nghiệp dự kiến hoặc có hoạt động thiết lập mạng viễn thông thực hiện.',
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

* Dataset: `dev_v5`
* Evaluated with [<code>CEBinaryClassificationEvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CEBinaryClassificationEvaluator)

| Metric                | Value      |
|:----------------------|:-----------|
| accuracy              | 0.71       |
| accuracy_threshold    | -0.6321    |
| f1                    | 0.7473     |
| f1_threshold          | -1.871     |
| precision             | 0.6321     |
| recall                | 0.914      |
| **average_precision** | **0.7657** |

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

* Size: 26,460 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                                      | sentence_1                                                                                        | label                                                          |
  |:--------|:------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                                          | string                                                                                            | float                                                          |
  | details | <ul><li>min: 26 characters</li><li>mean: 75.09 characters</li><li>max: 215 characters</li></ul> | <ul><li>min: 95 characters</li><li>mean: 483.91 characters</li><li>max: 2110 characters</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.27</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                            | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | label            |
  |:------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Việc thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không do ai quyết định?</code>      | <code>Khoản 3 Điều 6 NGHỊ ĐỊNH Giờ...... ĐẾN Quy định về phân cấp thẩm quyền quản lý nhà nước Ngày 13.16.2025 trong lĩnh vực quản lý, sử dụng tài sản công Bộ trưởng Bộ Xây dựng quyết định thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không quy định tại điểm a Khoản 2 Điều 17, điểm a khoản 12 Điều 18, điểm a khoản 2 Điều 19 Nghị định số 44/2018/NĐ-CP. Trình tự, thủ tục thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không thực hiện theo quy định tại khoản 5 Điều 17, khoản 4 Điều 18, khoản 5 Điều 19 Nghị định số 44/2018/NĐ-CP, không phải thực hiện việc báo cáo Thủ tướng Chính phủ xem xét, quyết định thu hồi, điều chuyển, bán tài sản kết cấu hạ tầng hàng không quy định tại điểm b khoản 5 Điều 17, điểm b Khoản 4 Điều 18; điểm b khoản 5 Điều 19 Nghị định số 44/2018/NĐ-CP.</code>                        | <code>1.0</code> |
  | <code>Việc lập báo cáo đề xuất chủ trương đầu tư dự án hỗ trợ kết cấu hạ tầng do ai thực hiện?</code> | <code>Khoản 8 Điều 12 NGHỊ ĐỊNH Quy định về phân định thẩm quyền của chính quyền địa phương cổng thông tin điện tử chính phủ 192 cấp trong lĩnh vực quản lý nhà nước của Bộ Xây dựng ĐẾN Ngày. 13.1.67.2025 Trách nhiệm tiếp nhận và công khai thông tin về dự án cải tạo, xây dựng lại nhà chung cư, tiếp nhận hồ sơ đăng ký tham gia làm chủ đầu tư dự án, phối hợp với Sở Xây dựng tổ chức lấy ý kiến các chủ sở hữu nhà chung cư, ký xác nhận biên bản lựa chọn chủ đầu tư dự án quy định tại khoản 2, khoản 3, khoản 4 khoản 5 và khoản 6 Điều 17 Nghị định số 98/2024/NĐ-CP ngày 25 tháng 7 năm 2024 của Chính phủ do Ủy ban nhân dân cấp xã thực hiện. phê duyệt phương án bồi thường, hỗ trợ tái định cư quy định khoản 9 Điều 18 Nghị định số 98/2024/NĐ-CP ngày 25 tháng 7 năm 202 4 của Chính phủ do Ủy ban nhân dân cấp xã thực hiện</code> | <code>0.0</code> |
  | <code>Phương châm của Nghị định này trong việc tiếp cận thông tin là gì?</code>                       | <code>Khoản 7 Điều 2 NGHỊ ĐỊNH Ngày 13.16.12025 Quy định về phân quyền, phân cấp trong lĩnh vực đối ngoại Bảo đảm quyền con người, quyền công dân, bảo đảm công khai, minh bạch, tạo điều kiện thuận lợi cho cá nhân, tổ chức trong việc tiếp cận thông tin, thực hiện các quyền, nghĩa vụ và các thủ tục theo quy định của pháp luật, không làm ảnh hưởng đến hoạt động bình thường của xã hội, người dân, doanh nghiệp.</code>                                                                                                                                                                                                                                                                                                                                                                                                                        | <code>0.0</code> |
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
| Epoch  | Step | Training Loss | dev_v5_average_precision |
|:------:|:----:|:-------------:|:------------------------:|
| 0.6046 | 500  | 0.7297        | -                        |
| 1.0    | 827  | -             | 0.7302                   |
| 1.2092 | 1000 | 0.4876        | -                        |
| 1.8138 | 1500 | 0.4585        | -                        |
| 2.0    | 1654 | -             | 0.7489                   |
| 2.4184 | 2000 | 0.4369        | -                        |
| 3.0    | 2481 | -             | 0.7652                   |
| 3.0230 | 2500 | 0.4296        | -                        |
| 3.6276 | 3000 | 0.4084        | -                        |
| 4.0    | 3308 | -             | 0.7631                   |
| 4.2322 | 3500 | 0.3980        | -                        |
| 4.8368 | 4000 | 0.3925        | -                        |
| 5.0    | 4135 | -             | 0.7657                   |


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