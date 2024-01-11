import numpy as np
import matplotlib.pyplot as plt

def compute_precision_recall(predictions, labels, confidence_threshold):
    # Sắp xếp các dự đoán theo xác suất từ cao đến thấp
    sorted_indices = np.argsort(predictions)[::-1]
    sorted_predictions = predictions[sorted_indices]
    sorted_labels = labels[sorted_indices]

    tp = 0  # True Positive
    fp = 0  # False Positive
    fn = np.sum(sorted_labels)  # False Negative (số lượng đối tượng thực tế)

    precision = []
    recall = []

    # Tính toán Precision và Recall cho từng ngưỡng xác suất
    for i in range(len(sorted_predictions)):
        if sorted_predictions[i] >= confidence_threshold:
            if sorted_labels[i] == 1:
                tp += 1
                fn -= 1
            else:
                fp += 1

        precision.append(tp / (tp + fp))
        recall.append(tp / (tp + fn))

    return np.array(precision), np.array(recall)

def compute_average_precision(precision, recall):
    # Phương pháp tiếp cận 1: Áp dụng xấp xỉ diện tích bằng các hình chữ nhật
    ap = 0
    for i in range(1, len(precision)):
        ap += (recall[i] - recall[i-1]) * precision[i]

    return ap

# Dữ liệu mô phỏng
num_samples = 100
predictions = np.random.rand(num_samples)  # Giả định kết quả dự đoán
labels = np.random.randint(2, size=num_samples)  # Giả định nhãn (ground truth)

# Tính toán Precision và Recall cho từng ngưỡng xác suất
confidence_thresholds = np.arange(0.1, 1, 0.05)
precision_list = []
recall_list = []

for threshold in confidence_thresholds:
    precision, recall = compute_precision_recall(predictions, labels, threshold)
    precision_list.append(precision)
    recall_list.append(recall)

# Vẽ Precision-Recall Curve
plt.figure()
plt.plot(recall_list, precision_list, marker='o')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.grid(True)
plt.show()

# Tính toán Average Precision (AP)
average_precisions = []
for i in range(len(confidence_thresholds)):
    ap = compute_average_precision(precision_list[i], recall_list[i])
    average_precisions.append(ap)

# Tính toán Mean Average Precision (mAP)
mAP = np.mean(average_precisions)

print("Average Precision (AP) for each confidence threshold:")
for i in range(len(confidence_thresholds)):
    print("Confidence threshold:", confidence_thresholds[i])
    print("AP:", average_precisions[i])
    print()

print("Mean Average Precision (mAP):", mAP)
