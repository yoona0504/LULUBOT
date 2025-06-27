import torch
import torch.nn as nn
from torchvision import models


class CBAM(nn.Module):
    def __init__(self, channels, reduction_ratio=16, kernel_size=7):
        super(CBAM, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)

        self.mlp = nn.Sequential(
            nn.Linear(channels, channels // reduction_ratio, bias=False),
            nn.ReLU(),
            nn.Linear(channels // reduction_ratio, channels, bias=False)
        )

        self.spatial = nn.Conv2d(2, 1, kernel_size=kernel_size, padding=kernel_size // 2)

    def forward(self, x):
        b, c, _, _ = x.size()
        avg_out = self.mlp(self.avg_pool(x).view(b, c))
        max_out = self.mlp(self.max_pool(x).view(b, c))
        scale = torch.sigmoid(avg_out + max_out).view(b, c, 1, 1)
        x = x * scale

        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        x = x * torch.sigmoid(self.spatial(torch.cat([avg_out, max_out], dim=1)))
        return x

class SEBlock(nn.Module):
    def __init__(self, channels, reduction=16):
        super(SEBlock, self).__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction),
            nn.ReLU(),
            nn.Linear(channels // reduction, channels),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y


class EmotionNet(nn.Module):
    def __init__(self, num_classes=7):
        super(EmotionNet, self).__init__()
        self.residual_block = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1), nn.ReLU(), nn.BatchNorm2d(64),
            nn.Conv2d(64, 64, kernel_size=3, padding=1), nn.ReLU(), nn.BatchNorm2d(64),
            nn.MaxPool2d(2)
        )
        self.attention_block = nn.Sequential(
            CBAM(3),
            nn.Conv2d(3, 64, kernel_size=3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.dilated_block = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, dilation=2, padding=2), nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, dilation=2, padding=2), nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.efficientnet = models.efficientnet_b0(pretrained=True)
        self.efficientnet.classifier = nn.Identity()

        self.fc = nn.Sequential(
            nn.Linear(1536, 512), nn.ReLU(), nn.Dropout(0.5),
            nn.Linear(512, 256), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(256, 128), nn.ReLU(), nn.Dropout(0.4),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x1 = self.residual_block(x)
        x1 = nn.AdaptiveAvgPool2d(1)(x1).view(x1.size(0), -1)

        x2 = self.attention_block(x)
        x2 = nn.AdaptiveAvgPool2d(1)(x2).view(x2.size(0), -1)

        x3 = self.dilated_block(x)
        x3 = nn.AdaptiveAvgPool2d(1)(x3).view(x3.size(0), -1)

        x4 = self.efficientnet(x)

        x = torch.cat((x1, x2, x3, x4), dim=1)
        return self.fc(x)