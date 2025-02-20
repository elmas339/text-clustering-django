from django.db import models


class TextClusteringResult(models.Model):
    file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    num_clusters = models.IntegerField()

    def __str__(self):
        return f"Clustering Result - {self.file_name}"


class ClusteredText(models.Model):
    result = models.ForeignKey(TextClusteringResult, on_delete=models.CASCADE)
    original_text = models.TextField()
    cluster_number = models.IntegerField()
    processed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Text in Cluster {self.cluster_number}"

    class Meta:
        verbose_name = "Clustered Text"
        verbose_name_plural = "Clustered Texts"