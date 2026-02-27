---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:22305
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
      value: 0.9375
      name: Accuracy
    - type: accuracy_threshold
      value: -0.5722813010215759
      name: Accuracy Threshold
    - type: f1
      value: 0.9340369393139841
      name: F1
    - type: f1_threshold
      value: -0.5722813010215759
      name: F1 Threshold
    - type: precision
      value: 0.9888268156424581
      name: Precision
    - type: recall
      value: 0.885
      name: Recall
    - type: average_precision
      value: 0.9825900428735848
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
    ['NGHỊ ĐỊNH Ngày.13.1.6.2025 Quy định về phân quyền, quy định những gì?', 'Khoản 1 Điều 16 Nhiệm vụ đang được cơ quan, người có thẩm quyền phân quyền, phân cấp thụ lý và đã thực hiện một phần nhưng chưa hoàn thành trước thời điểm Nghị định này có hiệu lực thì tiếp tục thực hiện, giải quyết.'],
    ['Nội dung Điều 16 là gì?', 'Tại điểm c Khoản 3 Điều 16 Báo cáo kết quả thực hiện nhiệm vụ phân quyền, phân cấp định kỳ trước ngày 31 tháng 12 hằng năm với cơ quan, người có thẩm quyền phân quyền, phân cấp;'],
    ['Trình tự thủ tục thực hiện như thế nào?', 'Khoản 3 Điều 15 Nhiệm vụ, quyền hạn của Văn phòng huyện ủy khi thực hiện trình tự, thủ tục thu hồi và xử lý, khai thác tài sản tại cơ quan của Đảng sau khi thu hồi được quy định tại khoản 3 Điều 24 Nghị định số 165/2017/NĐ-CP do Văn phòng tỉnh ủy thực hiện. Thuận hiện trình tự, thủ tục thu hồi và xử lý, khai thác tài sản tại cơ quan của Đảng sau khi thu hồi được quy định tại khoản 3 Điều 24 Nghị định số 165/2017/NĐ-CP do Sở Tài chính thực hiện.'],
    ['Trình tự thủ tục thực hiện như thế nào?', 'Khoản 2 Điều 4 Trình tự, thủ tục thực hiện thẩm định, phê duyệt phương án ứng phó thiên tai cho công trình hạ du đập thủy điện được quy định tại Phụ lục I ban hành kèm theo nghị định này.'],
    ['Nội dung Điều 79 là gì?', 'Khoản 2 Điều 14 Trình tự, thủ tục cấp, cấp lại, điều chỉnh Giấy chứng nhận đủ điều kiện cửa hàng bán lẻ LPG chai được quy định tại Phụ lục V ban hành kèm theo Nghị định này.'],
]
scores = model.predict(pairs)
print(scores.shape)
# (5,)

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'NGHỊ ĐỊNH Ngày.13.1.6.2025 Quy định về phân quyền, quy định những gì?',
    [
        'Khoản 1 Điều 16 Nhiệm vụ đang được cơ quan, người có thẩm quyền phân quyền, phân cấp thụ lý và đã thực hiện một phần nhưng chưa hoàn thành trước thời điểm Nghị định này có hiệu lực thì tiếp tục thực hiện, giải quyết.',
        'Tại điểm c Khoản 3 Điều 16 Báo cáo kết quả thực hiện nhiệm vụ phân quyền, phân cấp định kỳ trước ngày 31 tháng 12 hằng năm với cơ quan, người có thẩm quyền phân quyền, phân cấp;',
        'Khoản 3 Điều 15 Nhiệm vụ, quyền hạn của Văn phòng huyện ủy khi thực hiện trình tự, thủ tục thu hồi và xử lý, khai thác tài sản tại cơ quan của Đảng sau khi thu hồi được quy định tại khoản 3 Điều 24 Nghị định số 165/2017/NĐ-CP do Văn phòng tỉnh ủy thực hiện. Thuận hiện trình tự, thủ tục thu hồi và xử lý, khai thác tài sản tại cơ quan của Đảng sau khi thu hồi được quy định tại khoản 3 Điều 24 Nghị định số 165/2017/NĐ-CP do Sở Tài chính thực hiện.',
        'Khoản 2 Điều 4 Trình tự, thủ tục thực hiện thẩm định, phê duyệt phương án ứng phó thiên tai cho công trình hạ du đập thủy điện được quy định tại Phụ lục I ban hành kèm theo nghị định này.',
        'Khoản 2 Điều 14 Trình tự, thủ tục cấp, cấp lại, điều chỉnh Giấy chứng nhận đủ điều kiện cửa hàng bán lẻ LPG chai được quy định tại Phụ lục V ban hành kèm theo Nghị định này.',
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
| accuracy              | 0.9375     |
| accuracy_threshold    | -0.5723    |
| f1                    | 0.934      |
| f1_threshold          | -0.5723    |
| precision             | 0.9888     |
| recall                | 0.885      |
| **average_precision** | **0.9826** |

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

* Size: 22,305 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                                     | sentence_1                                                                                       | label                                                          |
  |:--------|:-----------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                                         | string                                                                                           | float                                                          |
  | details | <ul><li>min: 19 characters</li><li>mean: 34.54 characters</li><li>max: 69 characters</li></ul> | <ul><li>min: 61 characters</li><li>mean: 305.6 characters</li><li>max: 1482 characters</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.34</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                         | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | label            |
  |:-----------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>NGHỊ ĐỊNH Ngày.13.1.6.2025 Quy định về phân quyền, quy định những gì?</code> | <code>Khoản 1 Điều 16 Nhiệm vụ đang được cơ quan, người có thẩm quyền phân quyền, phân cấp thụ lý và đã thực hiện một phần nhưng chưa hoàn thành trước thời điểm Nghị định này có hiệu lực thì tiếp tục thực hiện, giải quyết.</code>                                                                                                                                                                                                                                         | <code>0.0</code> |
  | <code>Nội dung Điều 16 là gì?</code>                                               | <code>Tại điểm c Khoản 3 Điều 16 Báo cáo kết quả thực hiện nhiệm vụ phân quyền, phân cấp định kỳ trước ngày 31 tháng 12 hằng năm với cơ quan, người có thẩm quyền phân quyền, phân cấp;</code>                                                                                                                                                                                                                                                                                | <code>0.0</code> |
  | <code>Trình tự thủ tục thực hiện như thế nào?</code>                               | <code>Khoản 3 Điều 15 Nhiệm vụ, quyền hạn của Văn phòng huyện ủy khi thực hiện trình tự, thủ tục thu hồi và xử lý, khai thác tài sản tại cơ quan của Đảng sau khi thu hồi được quy định tại khoản 3 Điều 24 Nghị định số 165/2017/NĐ-CP do Văn phòng tỉnh ủy thực hiện. Thuận hiện trình tự, thủ tục thu hồi và xử lý, khai thác tài sản tại cơ quan của Đảng sau khi thu hồi được quy định tại khoản 3 Điều 24 Nghị định số 165/2017/NĐ-CP do Sở Tài chính thực hiện.</code> | <code>1.0</code> |
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
- `per_device_eval_batch_size`: 16
- `fp16`: True

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `overwrite_output_dir`: False
- `do_predict`: False
- `eval_strategy`: no
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `per_gpu_train_batch_size`: None
- `per_gpu_eval_batch_size`: None
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 3
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: {}
- `warmup_ratio`: 0.0
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `save_safetensors`: True
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `no_cuda`: False
- `use_cpu`: False
- `use_mps_device`: False
- `seed`: 42
- `data_seed`: None
- `jit_mode_eval`: False
- `use_ipex`: False
- `bf16`: False
- `fp16`: True
- `fp16_opt_level`: O1
- `half_precision_backend`: auto
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: 0
- `ddp_backend`: None
- `tpu_num_cores`: None
- `tpu_metrics_debug`: False
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `past_index`: -1
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_min_num_params`: 0
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `fsdp_transformer_layer_cls_to_wrap`: None
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch
- `optim_args`: None
- `adafactor`: False
- `group_by_length`: False
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `use_legacy_prediction_loop`: False
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: False
- `hub_always_push`: False
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_inputs_for_metrics`: False
- `eval_do_concat_batches`: True
- `fp16_backend`: auto
- `push_to_hub_model_id`: None
- `push_to_hub_organization`: None
- `mp_parameters`: 
- `auto_find_batch_size`: False
- `full_determinism`: False
- `torchdynamo`: None
- `ray_scope`: last
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `dispatch_batches`: None
- `split_batches`: None
- `include_tokens_per_second`: False
- `include_num_input_tokens_seen`: False
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `eval_use_gather_object`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss | dev_average_precision |
|:------:|:----:|:-------------:|:---------------------:|
| 0.3584 | 500  | 0.7904        | -                     |
| 0.7168 | 1000 | 0.3463        | -                     |
| 1.0    | 1395 | -             | 0.9578                |
| 1.0753 | 1500 | 0.2518        | -                     |
| 1.4337 | 2000 | 0.2076        | -                     |
| 1.7921 | 2500 | 0.1802        | -                     |
| 2.0    | 2790 | -             | 0.9834                |
| 2.1505 | 3000 | 0.1618        | -                     |
| 2.5090 | 3500 | 0.1567        | -                     |
| 2.8674 | 4000 | 0.1489        | -                     |
| 3.0    | 4185 | -             | 0.9826                |


### Framework Versions
- Python: 3.11.14
- Sentence Transformers: 5.2.2
- Transformers: 4.44.1
- PyTorch: 2.6.0+cu124
- Accelerate: 1.12.0
- Datasets: 4.4.1
- Tokenizers: 0.19.1

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