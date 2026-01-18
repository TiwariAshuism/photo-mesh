import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const ImageMeshApp());
}

class ImageMeshApp extends StatelessWidget {
  const ImageMeshApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Image Mesh AI',
      theme: ThemeData(primarySwatch: Colors.deepPurple, useMaterial3: true),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final ImagePicker _picker = ImagePicker();
  List<ImageData> images = [];
  bool isLoading = false;
  String? selectedFilter;

  final String backendUrl = 'http://10.0.2.2:8181';

  @override
  void initState() {
    super.initState();
    _loadImages();
  }

  Future<void> _loadImages() async {
    setState(() => isLoading = true);
    try {
      final response = await http.get(Uri.parse('$backendUrl/api/images'));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        setState(() {
          images = data.map((json) => ImageData.fromJson(json)).toList();
        });
      }
    } catch (e) {
      _showError('Failed to load images: $e');
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> _pickAndUploadImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image == null) return;

    setState(() => isLoading = true);
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$backendUrl/api/upload'));
      request.files.add(await http.MultipartFile.fromPath('image', image.path));

      var response = await request.send();
      if (response.statusCode == 200) {
        await _loadImages();
        _showSuccess('Image analyzed with AI! 🎨');
      }
    } catch (e) {
      _showError('Failed to upload: $e');
    } finally {
      setState(() => isLoading = false);
    }
  }

  List<ImageData> get filteredImages {
    if (selectedFilter == null) return images;
    return images
        .where(
          (img) =>
              img.tags.contains(selectedFilter) ||
              img.objects.any((obj) => obj.name.contains(selectedFilter!)) ||
              img.emotions.overallMood.contains(selectedFilter!),
        )
        .toList();
  }

  Set<String> get allFilters {
    Set<String> filters = {};
    for (var img in images) {
      filters.addAll(img.tags);
      filters.addAll(img.objects.map((o) => o.name));
      filters.add(img.emotions.overallMood);
      filters.add(img.emotions.vibe);
    }
    return filters;
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message), backgroundColor: Colors.red));
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message), backgroundColor: Colors.green));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Image Mesh AI'),
        actions: [
          IconButton(icon: const Icon(Icons.search), onPressed: () => _showSearchDialog()),
          IconButton(icon: const Icon(Icons.filter_alt), onPressed: () => _showFilterDialog()),
          IconButton(icon: const Icon(Icons.analytics), onPressed: () => _showStatsDialog()),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : filteredImages.isEmpty
          ? _buildEmptyState()
          : _buildImageGrid(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _pickAndUploadImage,
        icon: const Icon(Icons.add_photo_alternate),
        label: const Text('Add Image'),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.photo_library, size: 100, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text('No images yet', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          const Text('Upload images to see AI magic! ✨'),
        ],
      ),
    );
  }

  Widget _buildImageGrid() {
    return GridView.builder(
      padding: const EdgeInsets.all(8),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
        childAspectRatio: 0.75,
      ),
      itemCount: filteredImages.length,
      itemBuilder: (context, index) {
        final image = filteredImages[index];
        return _buildImageCard(image);
      },
    );
  }

  Widget _buildImageCard(ImageData image) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => _showImageDetails(image),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Image.network(
                    '$backendUrl${image.url}',
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(color: Colors.grey[300], child: const Icon(Icons.broken_image, size: 50));
                    },
                  ),
                  Positioned(
                    top: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(12)),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.mood, size: 16, color: Colors.white),
                          const SizedBox(width: 4),
                          Text(image.emotions.overallMood, style: const TextStyle(color: Colors.white, fontSize: 12)),
                        ],
                      ),
                    ),
                  ),
                  if (image.faces.isNotEmpty)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(color: Colors.purple.withOpacity(0.8), borderRadius: BorderRadius.circular(12)),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.face, size: 16, color: Colors.white),
                            const SizedBox(width: 4),
                            Text('${image.faces.length}', style: const TextStyle(color: Colors.white, fontSize: 12)),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (image.objects.isNotEmpty)
                    Text(
                      image.objects.take(2).map((o) => o.name).join(', '),
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  const SizedBox(height: 4),
                  if (image.scene.description.isNotEmpty)
                    Text(
                      image.scene.description,
                      style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showImageDetails(ImageData image) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.8,
        maxChildSize: 0.95,
        minChildSize: 0.5,
        expand: false,
        builder: (context, scrollController) {
          return SingleChildScrollView(
            controller: scrollController,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(color: Colors.grey[300], borderRadius: BorderRadius.circular(2)),
                    ),
                  ),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Image.network('$backendUrl${image.url}', width: double.infinity, fit: BoxFit.cover),
                  ),
                  const SizedBox(height: 16),

                  // AI Analysis Summary
                  _buildSectionHeader('🤖 AI Analysis', Icons.auto_awesome),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildInfoRow('Confidence', '${(image.confidence * 100).toStringAsFixed(1)}%'),
                          _buildInfoRow('Mood', image.emotions.overallMood),
                          _buildInfoRow('Vibe', image.emotions.vibe),
                          _buildInfoRow('Scene', image.scene.category),
                        ],
                      ),
                    ),
                  ),

                  // Objects Detected
                  if (image.objects.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    _buildSectionHeader('🎯 Objects Detected', Icons.visibility),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: image.objects
                          .map(
                            (obj) => Chip(
                              avatar: CircleAvatar(child: Text('${(obj.confidence * 100).toInt()}%', style: const TextStyle(fontSize: 8))),
                              label: Text(obj.name),
                            ),
                          )
                          .toList(),
                    ),
                  ],

                  // Faces & Emotions
                  if (image.faces.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    _buildSectionHeader('😊 Faces & Emotions', Icons.face),
                    ...image.faces.map(
                      (face) => Card(
                        child: Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Confidence: ${(face.confidence * 100).toStringAsFixed(1)}%'),
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 8,
                                children: face.emotions.entries
                                    .map((e) => Chip(label: Text('${e.key}: ${(e.value * 100).toInt()}%'), backgroundColor: _getEmotionColor(e.key)))
                                    .toList(),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],

                  // Scene Description
                  if (image.scene.description.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    _buildSectionHeader('🎬 Scene Understanding', Icons.landscape),
                    Card(
                      child: Padding(padding: const EdgeInsets.all(12.0), child: Text(image.scene.description)),
                    ),
                  ],

                  // Extracted Text
                  if (image.text.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    _buildSectionHeader('📝 Text Found', Icons.text_fields),
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: image.text.map((t) => Padding(padding: const EdgeInsets.only(bottom: 8.0), child: Text('• ${t.text}'))).toList(),
                        ),
                      ),
                    ),
                  ],

                  // Tags & Colors
                  const SizedBox(height: 16),
                  _buildSectionHeader('🏷️ Tags', Icons.label),
                  Wrap(spacing: 8, runSpacing: 8, children: image.tags.map((tag) => Chip(label: Text(tag))).toList()),

                  const SizedBox(height: 16),
                  _buildSectionHeader('🎨 Colors', Icons.palette),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: image.colors.map((color) => Chip(label: Text(color), backgroundColor: _getColorFromName(color))).toList(),
                  ),

                  // Related Images
                  if (image.relatedImages.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    _buildSectionHeader('🔗 Related Images', Icons.link),
                    SizedBox(
                      height: 120,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: image.relatedImages.length,
                        itemBuilder: (context, index) {
                          final relatedId = image.relatedImages[index];
                          final related = images.firstWhere((img) => img.id == relatedId, orElse: () => image);
                          return Padding(
                            padding: const EdgeInsets.only(right: 8.0),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: InkWell(
                                onTap: () {
                                  Navigator.pop(context);
                                  _showImageDetails(related);
                                },
                                child: Image.network('$backendUrl${related.url}', width: 120, fit: BoxFit.cover),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 8),
          Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0),
      child: Row(
        children: [
          Text('$label: ', style: const TextStyle(fontWeight: FontWeight.bold)),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  Color _getEmotionColor(String emotion) {
    switch (emotion.toLowerCase()) {
      case 'joy':
      case 'happy':
        return Colors.yellow.shade200;
      case 'sad':
      case 'sorrow':
        return Colors.blue.shade200;
      case 'anger':
        return Colors.red.shade200;
      case 'surprise':
        return Colors.orange.shade200;
      default:
        return Colors.grey.shade200;
    }
  }

  Color _getColorFromName(String colorName) {
    switch (colorName.toLowerCase()) {
      case 'red':
        return Colors.red.shade300;
      case 'blue':
        return Colors.blue.shade300;
      case 'green':
        return Colors.green.shade300;
      case 'yellow':
        return Colors.yellow.shade300;
      case 'black':
        return Colors.grey.shade800;
      case 'white':
        return Colors.grey.shade200;
      default:
        return Colors.grey.shade400;
    }
  }

  void _showSearchDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Search Images'),
        content: TextField(
          decoration: const InputDecoration(hintText: 'Search by objects, mood, tags...', prefixIcon: Icon(Icons.search)),
          onSubmitted: (value) {
            Navigator.pop(context);
            setState(() => selectedFilter = value);
          },
        ),
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filter Images'),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView(
            shrinkWrap: true,
            children: [
              ListTile(
                leading: const Icon(Icons.clear_all),
                title: const Text('All Images'),
                onTap: () {
                  Navigator.pop(context);
                  setState(() => selectedFilter = null);
                },
              ),
              const Divider(),
              ...allFilters.map(
                (filter) => ListTile(
                  title: Text(filter),
                  onTap: () {
                    Navigator.pop(context);
                    setState(() => selectedFilter = filter);
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showStatsDialog() async {
    try {
      final response = await http.get(Uri.parse('$backendUrl/api/stats'));
      if (response.statusCode == 200) {
        final stats = json.decode(response.body);
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('📊 Collection Statistics'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildStatRow('Total Images', '${stats['total_images']}'),
                _buildStatRow('Objects Detected', '${stats['total_objects']}'),
                _buildStatRow('Faces Found', '${stats['total_faces']}'),
                _buildStatRow('Unique Tags', '${stats['total_tags']}'),
                _buildStatRow('Avg Confidence', '${(stats['avg_confidence'] * 100).toStringAsFixed(1)}%'),
              ],
            ),
            actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
          ),
        );
      }
    } catch (e) {
      _showError('Failed to load stats');
    }
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
          Text(value, style: const TextStyle(fontSize: 16)),
        ],
      ),
    );
  }
}

// Data Models

class ImageData {
  final String id;
  final String url;
  final List<DetectedObject> objects;
  final List<FaceData> faces;
  final SceneAnalysis scene;
  final List<ExtractedText> text;
  final EmotionAnalysis emotions;
  final List<String> tags;
  final List<String> colors;
  final List<String> landmarks;
  final List<String> relatedImages;
  final double confidence;

  ImageData({
    required this.id,
    required this.url,
    required this.objects,
    required this.faces,
    required this.scene,
    required this.text,
    required this.emotions,
    required this.tags,
    required this.colors,
    required this.landmarks,
    required this.relatedImages,
    required this.confidence,
  });

  factory ImageData.fromJson(Map<String, dynamic> json) {
    return ImageData(
      id: json['id'] ?? '',
      url: json['url'] ?? '',
      objects: (json['objects'] as List?)?.map((o) => DetectedObject.fromJson(o)).toList() ?? [],
      faces: (json['faces'] as List?)?.map((f) => FaceData.fromJson(f)).toList() ?? [],
      scene: SceneAnalysis.fromJson(json['scene'] ?? {}),
      text: (json['text'] as List?)?.map((t) => ExtractedText.fromJson(t)).toList() ?? [],
      emotions: EmotionAnalysis.fromJson(json['emotions'] ?? {}),
      tags: List<String>.from(json['tags'] ?? []),
      colors: List<String>.from(json['colors'] ?? []),
      landmarks: List<String>.from(json['landmarks'] ?? []),
      relatedImages: List<String>.from(json['related_images'] ?? []),
      confidence: (json['confidence'] ?? 0.0).toDouble(),
    );
  }
}

class DetectedObject {
  final String name;
  final double confidence;

  DetectedObject({required this.name, required this.confidence});

  factory DetectedObject.fromJson(Map<String, dynamic> json) {
    return DetectedObject(name: json['name'] ?? '', confidence: (json['confidence'] ?? 0.0).toDouble());
  }
}

class FaceData {
  final double confidence;
  final Map<String, double> emotions;

  FaceData({required this.confidence, required this.emotions});

  factory FaceData.fromJson(Map<String, dynamic> json) {
    return FaceData(
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      emotions: Map<String, double>.from((json['emotions'] ?? {}).map((k, v) => MapEntry(k, v.toDouble()))),
    );
  }
}

class SceneAnalysis {
  final String description;
  final String category;

  SceneAnalysis({required this.description, required this.category});

  factory SceneAnalysis.fromJson(Map<String, dynamic> json) {
    return SceneAnalysis(description: json['description'] ?? '', category: json['category'] ?? '');
  }
}

class ExtractedText {
  final String text;
  final double confidence;

  ExtractedText({required this.text, required this.confidence});

  factory ExtractedText.fromJson(Map<String, dynamic> json) {
    return ExtractedText(text: json['text'] ?? '', confidence: (json['confidence'] ?? 0.0).toDouble());
  }
}

class EmotionAnalysis {
  final String overallMood;
  final String vibe;

  EmotionAnalysis({required this.overallMood, required this.vibe});

  factory EmotionAnalysis.fromJson(Map<String, dynamic> json) {
    return EmotionAnalysis(overallMood: json['overall_mood'] ?? 'neutral', vibe: json['vibe'] ?? 'balanced');
  }
}
