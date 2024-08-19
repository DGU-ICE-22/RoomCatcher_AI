from django.db import models

class DataAnalyzeTagDetail(models.Model):
    id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=64, primary_key=True)
    embedding = models.BinaryField()

    def __str__(self):
        return self.tag_name

class ReportAndRecommandUserType(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=64)
    type_explain = models.TextField()
    embedding = models.BinaryField()

    def __str__(self):
        return self.type_name

class UserTagCrossTable(models.Model):
    user_type = models.ForeignKey(ReportAndRecommandUserType, on_delete=models.CASCADE)
    tag = models.ForeignKey(DataAnalyzeTagDetail, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user_type', 'tag')