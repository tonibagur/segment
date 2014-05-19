function load_images(images)
X=[];
for i=1:size(images)
    imp=images{i}
    im=imread(imp)
    if size(size(i))==3:
        X=[X; im(:,:,1)(:)' im(:,:,2)(:)' im(:,:,3)(:)']
    else:
        X=[X;im(:)']
    end
end
